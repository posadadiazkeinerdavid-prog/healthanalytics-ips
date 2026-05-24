from django.contrib import admin
from .models import MLModel, Prediccion

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['model_type', 'accuracy', 'precision', 'recall', 'f1_score', 'total_samples', 'fecha_entrenamiento']

@admin.register(Prediccion)
class PrediccionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'riesgo_predicho', 'confianza', 'modelo_usado', 'fecha']
