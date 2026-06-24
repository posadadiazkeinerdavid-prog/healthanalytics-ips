from rest_framework import serializers
from .models import MLModel, Prediccion

class MLModelSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.full_name', read_only=True)
    class Meta:
        model = MLModel
        fields = '__all__'

class PrediccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediccion
        fields = '__all__'
