"""ML Models"""
from django.db import models
from django.conf import settings


class MLModel(models.Model):
    MODEL_TYPES = [
        ('random_forest', 'Random Forest'),
        ('logistic_regression', 'Regresión Logística'),
        ('decision_tree', 'Árbol de Decisión'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    total_samples = models.IntegerField(default=0)
    train_samples = models.IntegerField(default=0)
    test_samples = models.IntegerField(default=0)

    class Meta:
        db_table = 'ml_models'
        ordering = ['-fecha_entrenamiento']

    def __str__(self):
        return f'{self.model_type} - Acc:{self.accuracy:.4f} ({self.fecha_entrenamiento.date()})'


class Prediccion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    datos_entrada = models.JSONField()
    riesgo_predicho = models.CharField(max_length=20)
    confianza = models.FloatField()
    probabilidades = models.JSONField()
    modelo_usado = models.CharField(max_length=30)

    class Meta:
        db_table = 'ml_predicciones'
        ordering = ['-fecha']

    def __str__(self):
        return f'Predicción {self.riesgo_predicho} ({self.fecha.date()})'
