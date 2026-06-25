from rest_framework import serializers
from .models import MLModel, Prediccion


class MLModelSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = MLModel
        fields = '__all__'

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return obj.usuario.full_name
        return 'Sistema'


class PrediccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediccion
        fields = '__all__'