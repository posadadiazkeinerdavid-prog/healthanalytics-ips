"""
ETL Serializers - Paciente y ETLHistory
"""

from rest_framework import serializers
from .models import Paciente, ETLHistory


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ['fecha_registro', 'fecha_actualizacion', 'imc',
                            'imc_clasificacion', 'es_critico', 'es_hipertenso', 'es_diabetico']


class PacienteListSerializer(serializers.ModelSerializer):
    """Serializer compacto para listados"""
    class Meta:
        model = Paciente
        fields = [
            'id', 'id_paciente', 'nombres', 'apellidos', 'edad', 'sexo',
            'imc', 'imc_clasificacion', 'riesgo_enfermedad', 'diagnostico_preliminar',
            'es_critico', 'es_hipertenso', 'es_diabetico', 'fecha_consulta'
        ]


class ETLHistorySerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.full_name', read_only=True)

    class Meta:
        model = ETLHistory
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_fin']
