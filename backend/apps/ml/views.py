"""
ML Views - Entrenamiento, evaluación, predicción
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.authentication.permissions import IsAdminOrAnalista
from .services import train_model, predict_single, predict_batch, get_model_info
from .models import MLModel, Prediccion
from .serializers import MLModelSerializer, PrediccionSerializer


@api_view(['POST'])
@permission_classes([IsAdminOrAnalista])
def train_view(request):
    """Entrena el modelo ML seleccionado"""
    model_type = request.data.get('model_type', 'random_forest')
    valid_types = ['random_forest', 'logistic_regression', 'decision_tree']
    if model_type not in valid_types:
        return Response(
            {'error': f'model_type debe ser uno de: {valid_types}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        result = train_model(model_type)

        # Persistir registro del modelo
        MLModel.objects.create(
            usuario=request.user,
            model_type=model_type,
            accuracy=result['accuracy'],
            precision=result['precision'],
            recall=result['recall'],
            f1_score=result['f1_score'],
            total_samples=result['total_samples'],
            train_samples=result['train_samples'],
            test_samples=result['test_samples'],
        )

        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_view(request):
    """Predice riesgo para un paciente dado"""
    try:
        result = predict_single(request.data)

        # Guardar predicción
        Prediccion.objects.create(
            usuario=request.user,
            datos_entrada=request.data,
            riesgo_predicho=result['riesgo_predicho'],
            confianza=result['confianza'],
            probabilidades=result['probabilidades'],
            modelo_usado=result['modelo_usado'],
        )

        return Response(result)
    except FileNotFoundError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminOrAnalista])
def predict_batch_view(request):
    """Ejecuta predicción batch sobre todos los pacientes"""
    try:
        result = predict_batch()
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_info_view(request):
    """Información del modelo activo"""
    return Response(get_model_info())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_history_view(request):
    """Historial de modelos entrenados"""
    models = MLModel.objects.all().order_by('-fecha_entrenamiento')[:20]
    serializer = MLModelSerializer(models, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def predicciones_history_view(request):
    """Historial de predicciones"""
    preds = Prediccion.objects.filter(usuario=request.user).order_by('-fecha')[:50]
    serializer = PrediccionSerializer(preds, many=True)
    return Response(serializer.data)
