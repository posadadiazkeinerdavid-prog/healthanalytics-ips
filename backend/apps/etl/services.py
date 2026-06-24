"""
ETL Service - Extract, Transform, Load Engine
Motor ETL para datos clínicos
"""

import logging
import time
import re
from datetime import datetime, date
from typing import Tuple, Dict, Any

import pandas as pd
import numpy as np
from django.db import transaction
from django.conf import settings

from .models import Paciente, ETLHistory

logger = logging.getLogger('apps.etl')


# ─── NORMALIZACIÓN ─────────────────────────────────────────────────────────────

SEXO_MAP = {
    'm': 'M', 'masculino': 'M', 'hombre': 'M', 'male': 'M',
    'f': 'F', 'femenino': 'F', 'mujer': 'F', 'female': 'F',
}

DIAGNOSTICO_MAP = {
    'hipertencion': 'Hipertensión',
    'hipertensíon': 'Hipertensión',
    'hipertension': 'Hipertensión',
    'hipertensión': 'Hipertensión',
    'paciente sano': 'Paciente sano',
    'sano': 'Paciente sano',
    'diabetes tipo 2': 'Diabetes Tipo 2',
    'diabetes': 'Diabetes Tipo 2',
    'obesidad': 'Obesidad',
    'prehipertensión': 'Prehipertensión',
    'prehipertension': 'Prehipertensión',
    'riesgo cardiovascular': 'Riesgo cardiovascular',
    'cardiopatía': 'Cardiopatía',
    'cardiopatia': 'Cardiopatía',
}

ACTIVIDAD_MAP = {
    'sedentario': 'Sedentario',
    'baja': 'Baja',
    'media': 'Media',
    'moderada': 'Media',
    'alta': 'Alta',
    'muy alta': 'Alta',
}

RIESGO_MAP = {
    'bajo': 'Bajo',
    'medio': 'Medio',
    'alto': 'Alto',
    'crítico': 'Crítico',
    'critico': 'Crítico',
}

VALID_DIAGNOSTICOS = {
    'Paciente sano', 'Prehipertensión', 'Hipertensión',
    'Diabetes Tipo 2', 'Obesidad', 'Riesgo cardiovascular', 'Cardiopatía'
}

# Rangos clínicos válidos
CLINICAL_RANGES = {
    'edad': (0, 120),
    'peso': (2, 300),
    'altura': (0.3, 2.5),
    'presion_sistolica': (60, 250),
    'presion_diastolica': (40, 150),
    'frecuencia_cardiaca': (30, 220),
    'glucosa': (50, 600),
    'colesterol': (50, 600),
    'saturacion_oxigeno': (50, 100),
    'temperatura': (30, 43),
}


class ETLService:
    """Servicio ETL principal - maneja Extract, Transform y Load"""

    def __init__(self):
        self.log_lines = []
        self.stats = {
            'extraidos': 0,
            'duplicados': 0,
            'nulos_tratados': 0,
            'invalidos': 0,
            'cargados': 0,
        }

    def _log(self, msg: str, level: str = 'INFO'):
        ts = datetime.now().strftime('%H:%M:%S')
        line = f'[{ts}] [{level}] {msg}'
        self.log_lines.append(line)
        if level == 'ERROR':
            logger.error(msg)
        else:
            logger.info(msg)

    # ─── EXTRACT ────────────────────────────────────────────────────────────────

    def extract_from_excel(self, filepath: str) -> pd.DataFrame:
        self._log(f'EXTRACT: Leyendo archivo Excel: {filepath}')
        start = time.time()
        try:
            df = pd.read_excel(filepath, engine='openpyxl')
            elapsed = round(time.time() - start, 2)
            self._log(f'EXTRACT: {len(df)} registros leídos en {elapsed}s')
            self.stats['extraidos'] = len(df)
            return df
        except Exception as e:
            self._log(f'EXTRACT ERROR: {e}', 'ERROR')
            raise

    def extract_from_csv(self, filepath: str) -> pd.DataFrame:
        self._log(f'EXTRACT: Leyendo archivo CSV: {filepath}')
        start = time.time()
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='latin-1')
        elapsed = round(time.time() - start, 2)
        self._log(f'EXTRACT: {len(df)} registros leídos en {elapsed}s')
        self.stats['extraidos'] = len(df)
        return df

    # ─── TRANSFORM ──────────────────────────────────────────────────────────────

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self._log('TRANSFORM: Iniciando transformación de datos...')
        df = df.copy()

        # 1. Renombrar columnas a nombres internos
        df = self._rename_columns(df)

        # 2. Eliminar duplicados
        df = self._remove_duplicates(df)

        # 3. Convertir tipos
        df = self._convert_types(df)

        # 4. Validar y limpiar rangos clínicos
        df = self._validate_clinical_ranges(df)

        # 5. Tratar valores nulos
        df = self._handle_nulls(df)

        # 6. Normalizar variables categóricas
        df = self._normalize_categoricals(df)

        # 7. Calcular IMC
        df = self._calculate_imc(df)

        # 8. Clasificar riesgo
        df = self._classify_risk(df)

        self._log(f'TRANSFORM: Completado. {len(df)} registros válidos')
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza nombres de columnas — acepta tildes, mayúsculas, espacios, guiones"""
        import unicodedata

        def normalize(s):
            """Quita tildes, pasa a minúscula, reemplaza espacios/guiones por _"""
            s = str(s).strip().lower()
            s = unicodedata.normalize('NFD', s)
            s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
            s = re.sub(r'[\s\-]+', '_', s)
            return s

        # Mapa de nombre normalizado → nombre interno del modelo
        CANONICAL = {
            'id_paciente': 'id_paciente',
            'nombres': 'nombres',
            'apellidos': 'apellidos',
            'edad': 'edad',
            'sexo': 'sexo',
            'peso': 'peso',
            'altura': 'altura',
            'imc': 'imc',
            'presion_sistolica': 'presion_sistolica',
            'presion_diastolica': 'presion_diastolica',
            'frecuencia_cardiaca': 'frecuencia_cardiaca',
            'glucosa': 'glucosa',
            'colesterol': 'colesterol',
            'saturacion_oxigeno': 'saturacion_oxigeno',
            'temperatura': 'temperatura',
            'antecedentes_familiares': 'antecedentes_familiares',
            'fumador': 'fumador',
            'consumo_alcohol': 'consumo_alcohol',
            'actividad_fisica': 'actividad_fisica',
            'diagnostico_preliminar': 'diagnostico_preliminar',
            'riesgo_enfermedad': 'riesgo_enfermedad',
            'fecha_consulta': 'fecha_consulta',
        }

        rename_map = {}
        for col in df.columns:
            key = normalize(col)
            if key in CANONICAL:
                rename_map[col] = CANONICAL[key]

        df = df.rename(columns=rename_map)
        found = list(rename_map.values())
        missing = [c for c in CANONICAL if c not in df.columns]
        if missing:
            self._log(f'TRANSFORM: Columnas no encontradas en el archivo: {missing}', 'WARNING')
        self._log(f'TRANSFORM: Columnas mapeadas: {found}')
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates(subset=['id_paciente'], keep='first')
        removed = before - len(df)
        self.stats['duplicados'] = removed
        self._log(f'TRANSFORM: {removed} duplicados eliminados')
        return df

    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        self._log('TRANSFORM: Convirtiendo tipos de datos...')

        # edad → int (puede venir como string "Treinta")
        def safe_int_age(val):
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return np.nan

        if 'edad' in df.columns:
            df['edad'] = df['edad'].apply(safe_int_age)

        # presion_sistolica → int (puede venir como "Alta")
        def safe_int(val):
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return np.nan

        for col in ['presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca']:
            if col in df.columns:
                df[col] = df[col].apply(safe_int)

        # glucosa, colesterol, etc → float
        for col in ['glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura', 'peso', 'altura', 'imc']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # booleans
        for col in ['antecedentes_familiares', 'fumador', 'consumo_alcohol']:
            if col in df.columns:
                df[col] = df[col].map(
                    lambda x: True if str(x).lower() in ['true', '1', 'si', 'sí', 'yes'] else False
                )

        # fechas
        if 'fecha_consulta' in df.columns:
            df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'], errors='coerce').dt.date

        return df

    def _validate_clinical_ranges(self, df: pd.DataFrame) -> pd.DataFrame:
        self._log('TRANSFORM: Validando rangos clínicos...')
        col_map = {
            'edad': 'edad',
            'peso': 'peso',
            'altura': 'altura',
            'presion_sistolica': 'presion_sistolica',
            'presion_diastolica': 'presion_diastolica',
            'frecuencia_cardiaca': 'frecuencia_cardiaca',
            'glucosa': 'glucosa',
            'colesterol': 'colesterol',
            'saturacion_oxigeno': 'saturacion_oxigeno',
            'temperatura': 'temperatura',
        }
        for col, range_key in col_map.items():
            if col in df.columns and range_key in CLINICAL_RANGES:
                lo, hi = CLINICAL_RANGES[range_key]
                mask = (df[col] < lo) | (df[col] > hi)
                count = mask.sum()
                if count > 0:
                    self._log(f'TRANSFORM: {count} valores fuera de rango en {col} → NaN')
                    df.loc[mask, col] = np.nan
                    self.stats['invalidos'] += int(count)
        return df

    def _handle_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        self._log('TRANSFORM: Tratando valores nulos...')
        null_before = df.isnull().sum().sum()

        # Numéricos → media
        for col in ['peso', 'glucosa', 'colesterol', 'temperatura', 'imc']:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mean())

        # Enteros → mediana (round before cast to avoid float→int errors)
        for col in ['edad', 'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca']:
            if col in df.columns:
                median_val = df[col].median()
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(median_val).round(0).astype(float)

        # Saturación y altura → media clínica si falta
        if 'saturacion_oxigeno' in df.columns:
            df['saturacion_oxigeno'] = df['saturacion_oxigeno'].fillna(97.0)
        if 'altura' in df.columns:
            df['altura'] = df['altura'].fillna(df['altura'].mean())

        # Categóricos → moda
        for col in ['sexo', 'actividad_fisica', 'diagnostico_preliminar', 'riesgo_enfermedad']:
            if col in df.columns:
                mode = df[col].mode()
                if len(mode) > 0:
                    df[col] = df[col].fillna(mode[0])

        # Booleanos → False
        for col in ['antecedentes_familiares', 'fumador', 'consumo_alcohol']:
            if col in df.columns:
                df[col] = df[col].fillna(False)

        # Fecha → hoy
        if 'fecha_consulta' in df.columns:
            df['fecha_consulta'] = df['fecha_consulta'].apply(
                lambda x: x if pd.notna(x) else date.today()
            )

        null_after = df.isnull().sum().sum()
        self.stats['nulos_tratados'] = int(null_before - null_after)
        self._log(f'TRANSFORM: {self.stats["nulos_tratados"]} valores nulos tratados')
        return df

    def _normalize_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        self._log('TRANSFORM: Normalizando variables categóricas...')

        if 'sexo' in df.columns:
            df['sexo'] = df['sexo'].astype(str).str.strip().str.lower().map(SEXO_MAP).fillna('M')

        if 'diagnostico_preliminar' in df.columns:
            df['diagnostico_preliminar'] = (
                df['diagnostico_preliminar']
                .astype(str).str.strip().str.lower()
                .map(lambda x: DIAGNOSTICO_MAP.get(x, x.title()))
            )
            # Si aún no está en válidos → 'Paciente sano'
            df['diagnostico_preliminar'] = df['diagnostico_preliminar'].apply(
                lambda x: x if x in VALID_DIAGNOSTICOS else 'Paciente sano'
            )

        if 'actividad_fisica' in df.columns:
            df['actividad_fisica'] = (
                df['actividad_fisica']
                .astype(str).str.strip().str.lower()
                .map(lambda x: ACTIVIDAD_MAP.get(x, 'Media'))
            )

        if 'riesgo_enfermedad' in df.columns:
            df['riesgo_enfermedad'] = (
                df['riesgo_enfermedad']
                .astype(str).str.strip().str.lower()
                .map(lambda x: RIESGO_MAP.get(x, 'Bajo'))
            )

        return df

    def _calculate_imc(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'peso' in df.columns and 'altura' in df.columns:
            mask = (df['altura'] > 0) & df['peso'].notna() & df['altura'].notna()
            df.loc[mask, 'imc'] = (df.loc[mask, 'peso'] / (df.loc[mask, 'altura'] ** 2)).round(2)
            self._log('TRANSFORM: IMC recalculado')
        return df

    def _classify_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reclasifica riesgo basado en reglas clínicas"""
        def compute_risk(row):
            # Crítico
            if (row.get('presion_sistolica', 0) > 180 or
                    row.get('glucosa', 0) > 300 or
                    row.get('saturacion_oxigeno', 100) < 85):
                return 'Crítico'
            # Alto
            imc = row.get('imc', 0) or 0
            if (row.get('presion_sistolica', 0) >= 160 or
                    row.get('glucosa', 0) >= 200 or
                    imc >= 35):
                return 'Alto'
            # Medio
            if (row.get('presion_sistolica', 0) >= 140 or
                    row.get('glucosa', 0) >= 126 or
                    imc >= 30 or
                    row.get('colesterol', 0) >= 240):
                return 'Medio'
            return 'Bajo'

        df['riesgo_enfermedad'] = df.apply(compute_risk, axis=1)
        self._log('TRANSFORM: Clasificación de riesgo aplicada')
        return df

    # ─── LOAD ───────────────────────────────────────────────────────────────────

    def load(self, df: pd.DataFrame) -> int:
        self._log(f'LOAD: Iniciando carga de {len(df)} registros...')
        start = time.time()
        loaded = 0
        errors = 0

        df = df.drop_duplicates(subset=['id_paciente'], keep='last')
        total = len(df)
        self._log(f'LOAD: {total} registros únicos tras limpieza de duplicados en el archivo')

        if total == 0:
            self._log('LOAD: Sin registros para cargar')
            self.stats['cargados'] = 0
            return 0

        ids = [int(i) for i in df['id_paciente'].tolist() if pd.notna(i) and int(i) > 0]
        if ids:
            existing = Paciente.objects.filter(id_paciente__in=ids)
            self._log(f'LOAD: Eliminando {existing.count()} registros existentes para evitar duplicados')
            existing.delete()

        BATCH_SIZE = 100
        processed_ids = set()

        for batch_start in range(0, total, BATCH_SIZE):
            batch = df.iloc[batch_start:batch_start + BATCH_SIZE]
            try:
                with transaction.atomic():
                    for _, row in batch.iterrows():
                        try:
                            p_obj = self._row_to_paciente(row)
                            pid = p_obj.id_paciente
                            if pid in processed_ids or pid <= 0:
                                if pid <= 0:
                                    self._log(f'LOAD: id_paciente inválido ({pid}), saltando', 'WARNING')
                                else:
                                    self._log(f'LOAD: id_paciente {pid} repetido en el archivo, saltando', 'WARNING')
                                continue
                            processed_ids.add(pid)
                            Paciente.objects.update_or_create(
                                id_paciente=pid,
                                defaults={
                                    'nombres': p_obj.nombres,
                                    'apellidos': p_obj.apellidos,
                                    'edad': p_obj.edad,
                                    'sexo': p_obj.sexo,
                                    'peso': p_obj.peso,
                                    'altura': p_obj.altura,
                                    'imc': p_obj.imc,
                                    'imc_clasificacion': p_obj.imc_clasificacion,
                                    'presion_sistolica': p_obj.presion_sistolica,
                                    'presion_diastolica': p_obj.presion_diastolica,
                                    'frecuencia_cardiaca': p_obj.frecuencia_cardiaca,
                                    'glucosa': p_obj.glucosa,
                                    'colesterol': p_obj.colesterol,
                                    'saturacion_oxigeno': p_obj.saturacion_oxigeno,
                                    'temperatura': p_obj.temperatura,
                                    'antecedentes_familiares': p_obj.antecedentes_familiares,
                                    'fumador': p_obj.fumador,
                                    'consumo_alcohol': p_obj.consumo_alcohol,
                                    'actividad_fisica': p_obj.actividad_fisica,
                                    'diagnostico_preliminar': p_obj.diagnostico_preliminar,
                                    'riesgo_enfermedad': p_obj.riesgo_enfermedad,
                                    'fecha_consulta': p_obj.fecha_consulta,
                                    'es_critico': p_obj.es_critico,
                                    'es_hipertenso': p_obj.es_hipertenso,
                                    'es_diabetico': p_obj.es_diabetico,
                                }
                            )
                            loaded += 1
                        except Exception as e:
                            errors += 1
                            self._log(f'LOAD ERROR ID {row.get("id_paciente")}: {e}', 'ERROR')
            except Exception as e:
                self._log(f'LOAD BATCH ERROR lote {batch_start}: {e}', 'ERROR')

        elapsed = round(time.time() - start, 2)
        self.stats['cargados'] = loaded
        self._log(f'LOAD FINALIZADO: {loaded} registros procesados, {errors} errores en {elapsed}s')
        return loaded

    def _row_to_paciente(self, row) -> Paciente:
        def safe(val, default=None):
            if pd.isna(val) if not isinstance(val, (str, bool, date)) else False:
                return default
            return val

        def safe_float(val, default=0.0):
            try:
                return float(val)
            except (TypeError, ValueError):
                return default

        def safe_int(val, default=0):
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        imc = safe_float(row.get('imc'))
        peso = safe_float(row.get('peso'))
        altura = safe_float(row.get('altura'), 1.70)

        if imc == 0 and peso > 0 and altura > 0:
            imc = round(peso / (altura ** 2), 2)

        imc_cls = None
        if imc:
            if imc < 18.5:
                imc_cls = 'Bajo peso'
            elif imc <= 24.9:
                imc_cls = 'Normal'
            elif imc <= 29.9:
                imc_cls = 'Sobrepeso'
            else:
                imc_cls = 'Obesidad'

        presion_s = safe_int(row.get('presion_sistolica'), 120)
        glucosa = safe_float(row.get('glucosa'), 90.0)
        sat = safe_float(row.get('saturacion_oxigeno'), 97.0)

        p = Paciente(
            id_paciente=safe_int(row.get('id_paciente')),
            nombres=str(row.get('nombres', '')).strip().title(),
            apellidos=str(row.get('apellidos', '')).strip().title(),
            edad=safe_int(row.get('edad'), 30),
            sexo=str(row.get('sexo', 'M')).upper()[:1],
            peso=peso or 70.0,
            altura=altura,
            imc=imc,
            imc_clasificacion=imc_cls,
            presion_sistolica=presion_s,
            presion_diastolica=safe_int(row.get('presion_diastolica'), 80),
            frecuencia_cardiaca=safe_int(row.get('frecuencia_cardiaca'), 75),
            glucosa=glucosa,
            colesterol=safe_float(row.get('colesterol'), 180.0),
            saturacion_oxigeno=sat,
            temperatura=safe_float(row.get('temperatura'), 36.5),
            antecedentes_familiares=bool(row.get('antecedentes_familiares', False)),
            fumador=bool(row.get('fumador', False)),
            consumo_alcohol=bool(row.get('consumo_alcohol', False)),
            actividad_fisica=str(row.get('actividad_fisica', 'Media')),
            diagnostico_preliminar=str(row.get('diagnostico_preliminar', 'Paciente sano')),
            riesgo_enfermedad=str(row.get('riesgo_enfermedad', 'Bajo')),
            fecha_consulta=row.get('fecha_consulta') or date.today(),
            es_critico=(presion_s > 180 or glucosa > 300 or sat < 85),
            es_hipertenso=(presion_s >= 140 or safe_int(row.get('presion_diastolica'), 80) >= 90),
            es_diabetico=(glucosa >= 126),
        )
        return p

    # ─── RUN FULL ETL ────────────────────────────────────────────────────────────

    def run(self, filepath: str, source_type: str = 'EXCEL_UPLOAD',
            etl_record: ETLHistory = None) -> Dict[str, Any]:
        """Ejecuta el pipeline ETL completo"""
        start = time.time()
        self._log(f'═══ INICIO ETL ══════════════════════════════════')
        self._log(f'Fuente: {filepath} | Tipo: {source_type}')

        try:
            # EXTRACT
            if filepath.endswith('.csv'):
                df = self.extract_from_csv(filepath)
            else:
                df = self.extract_from_excel(filepath)

            # TRANSFORM
            df_clean = self.transform(df)

            # LOAD
            loaded = self.load(df_clean)

            elapsed = round(time.time() - start, 2)
            self._log(f'═══ ETL COMPLETADO en {elapsed}s ═══════════════')

            result = {
                'status': 'COMPLETADO',
                'tiempo_ejecucion': elapsed,
                'registros_extraidos': self.stats['extraidos'],
                'registros_duplicados': self.stats['duplicados'],
                'registros_invalidos': self.stats['invalidos'],
                'registros_nulos_tratados': self.stats['nulos_tratados'],
                'registros_cargados': loaded,
                'log': '\n'.join(self.log_lines),
            }

            if etl_record:
                from django.utils import timezone
                etl_record.fecha_fin = timezone.now()
                etl_record.tiempo_ejecucion = elapsed
                etl_record.registros_extraidos = self.stats['extraidos']
                etl_record.registros_duplicados = self.stats['duplicados']
                etl_record.registros_invalidos = self.stats['invalidos']
                etl_record.registros_cargados = loaded
                etl_record.estado = 'COMPLETADO'
                etl_record.log_detalle = '\n'.join(self.log_lines)
                etl_record.save()

            return result

        except Exception as e:
            elapsed = round(time.time() - start, 2)
            self._log(f'ERROR CRÍTICO: {e}', 'ERROR')

            if etl_record:
                from django.utils import timezone
                etl_record.fecha_fin = timezone.now()
                etl_record.tiempo_ejecucion = elapsed
                etl_record.estado = 'ERROR'
                etl_record.mensaje_error = str(e)
                etl_record.log_detalle = '\n'.join(self.log_lines)
                etl_record.save()

            return {
                'status': 'ERROR',
                'tiempo_ejecucion': elapsed,
                'error': str(e),
                'log': '\n'.join(self.log_lines),
            }
