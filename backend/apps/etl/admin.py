from django.contrib import admin
from .models import Paciente, ETLHistory

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['id_paciente', 'nombres', 'apellidos', 'edad', 'sexo', 'riesgo_enfermedad', 'es_critico', 'diagnostico_preliminar']
    list_filter = ['riesgo_enfermedad', 'sexo', 'es_critico', 'diagnostico_preliminar']
    search_fields = ['nombres', 'apellidos', 'id_paciente']
    ordering = ['-fecha_registro']

@admin.register(ETLHistory)
class ETLHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'fuente', 'estado', 'registros_cargados', 'tiempo_ejecucion', 'fecha_inicio']
    list_filter = ['estado', 'fuente']
    readonly_fields = ['fecha_inicio', 'fecha_fin', 'log_detalle']
