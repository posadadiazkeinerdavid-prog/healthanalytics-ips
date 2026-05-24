"""
Machine Learning Service
Entrenamiento, evaluación y predicción de riesgo clínico
"""

import logging
import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.pipeline import Pipeline

logger = logging.getLogger('apps.ml')

# Variables predictoras
FEATURE_COLS = [
    'imc', 'edad', 'glucosa', 'colesterol',
    'presion_sistolica', 'presion_diastolica',
    'frecuencia_cardiaca', 'fumador',
    'antecedentes_familiares', 'consumo_alcohol',
    'saturacion_oxigeno', 'temperatura',
]

TARGET_COL = 'riesgo_enfermedad'
RIESGO_LABELS = ['Bajo', 'Medio', 'Alto', 'Crítico']

MODELS_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
os.makedirs(MODELS_DIR, exist_ok=True)


def _model_path(name: str) -> str:
    return os.path.join(MODELS_DIR, f'{name}.joblib')


def _get_dataframe() -> pd.DataFrame:
    from apps.etl.models import Paciente
    qs = Paciente.objects.values(*FEATURE_COLS, TARGET_COL)
    df = pd.DataFrame(list(qs))
    return df


def _prepare_data(df: pd.DataFrame):
    """Preprocesa features y target para ML"""
    df = df.copy()

    # Booleanos a int
    for col in ['fumador', 'antecedentes_familiares', 'consumo_alcohol']:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # Nulos → media
    for col in FEATURE_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(df[col].median())

    # Encode target
    le = LabelEncoder()
    le.classes_ = np.array(RIESGO_LABELS)
    df[TARGET_COL] = df[TARGET_COL].apply(
        lambda x: x if x in RIESGO_LABELS else 'Bajo'
    )
    y = le.transform(df[TARGET_COL])

    X = df[FEATURE_COLS].values
    return X, y, le


def train_model(model_type: str = 'random_forest') -> dict:
    """
    Entrena el modelo ML especificado y guarda en disco.
    model_type: 'random_forest' | 'logistic_regression' | 'decision_tree'
    """
    df = _get_dataframe()
    if df.empty or len(df) < 50:
        raise ValueError('No hay suficientes datos. Ejecute el ETL primero.')

    X, y, le = _prepare_data(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    if model_type == 'random_forest':
        clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        pipeline = Pipeline([('clf', clf)])
    elif model_type == 'logistic_regression':
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(max_iter=500, random_state=42))
        ])
    elif model_type == 'decision_tree':
        clf = DecisionTreeClassifier(max_depth=8, random_state=42)
        pipeline = Pipeline([('clf', clf)])
    else:
        raise ValueError(f'Modelo no soportado: {model_type}')

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    # Métricas
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
    rec = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True, zero_division=0)

    # Feature importance (si aplica)
    feature_importance = {}
    estimator = pipeline.named_steps.get('clf')
    if hasattr(estimator, 'feature_importances_'):
        feature_importance = dict(zip(FEATURE_COLS, estimator.feature_importances_.tolist()))

    # Guardar modelo y encoder
    joblib.dump(pipeline, _model_path(model_type))
    joblib.dump(le, _model_path('label_encoder'))

    # Guardar último modelo usado
    joblib.dump({'last': model_type}, _model_path('metadata'))

    logger.info(f'Modelo {model_type} entrenado. Accuracy={acc:.4f}')

    return {
        'model_type': model_type,
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'total_samples': len(X),
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm,
        'confusion_matrix_labels': RIESGO_LABELS,
        'classification_report': report,
        'feature_importance': feature_importance,
        'feature_cols': FEATURE_COLS,
    }


def predict_single(data: dict) -> dict:
    """Predice riesgo para un solo paciente"""
    # Cargar modelo
    meta_path = _model_path('metadata')
    if not os.path.exists(meta_path):
        raise FileNotFoundError('No hay modelo entrenado. Entrene un modelo primero.')

    meta = joblib.load(meta_path)
    model_type = meta['last']
    pipeline = joblib.load(_model_path(model_type))
    le = joblib.load(_model_path('label_encoder'))

    # Preparar features
    row = []
    for col in FEATURE_COLS:
        val = data.get(col, 0)
        if isinstance(val, bool):
            val = int(val)
        row.append(float(val) if val is not None else 0.0)

    X = np.array([row])
    pred_idx = pipeline.predict(X)[0]
    probas = pipeline.predict_proba(X)[0]

    riesgo = le.inverse_transform([pred_idx])[0]
    probas_dict = {label: round(float(p), 4) for label, p in zip(le.classes_, probas)}

    return {
        'riesgo_predicho': riesgo,
        'probabilidades': probas_dict,
        'modelo_usado': model_type,
        'confianza': round(float(probas.max()), 4),
    }


def predict_batch() -> dict:
    """Predice riesgo para todos los pacientes en BD y actualiza el campo"""
    from apps.etl.models import Paciente

    meta_path = _model_path('metadata')
    if not os.path.exists(meta_path):
        raise FileNotFoundError('No hay modelo entrenado.')

    meta = joblib.load(meta_path)
    model_type = meta['last']
    pipeline = joblib.load(_model_path(model_type))
    le = joblib.load(_model_path('label_encoder'))

    df = _get_dataframe()
    if df.empty:
        raise ValueError('No hay pacientes cargados.')

    X, _, _ = _prepare_data(df)
    preds = pipeline.predict(X)
    labels = le.inverse_transform(preds)

    # Stats de predicciones
    from collections import Counter
    counts = Counter(labels)

    return {
        'total_predichos': len(labels),
        'distribucion': dict(counts),
        'modelo_usado': model_type,
    }


def get_model_info() -> dict:
    """Información del modelo entrenado"""
    meta_path = _model_path('metadata')
    if not os.path.exists(meta_path):
        return {'entrenado': False}

    meta = joblib.load(meta_path)
    model_type = meta['last']
    path = _model_path(model_type)
    size = os.path.getsize(path) if os.path.exists(path) else 0

    return {
        'entrenado': True,
        'modelo_activo': model_type,
        'tamaño_bytes': size,
        'variables_predictoras': FEATURE_COLS,
        'clases': RIESGO_LABELS,
    }
