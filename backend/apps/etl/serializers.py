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
            'es_critico', 'es_hipertenso', 'es_diabetico', 'fecha_consulta',
            'presion_sistolica', 'glucosa', 'saturacion_oxigeno'
        ]


class ETLHistorySerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ETLHistory
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_fin']

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return obj.usuario.full_name
        return 'Sistema'