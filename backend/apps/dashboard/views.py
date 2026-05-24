"""
Dashboard Views - KPIs combinados para el panel principal
"""

from django.db.models import Count, Avg, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.etl.models import Paciente, ETLHistory
from apps.ml.models import MLModel, Prediccion


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_kpis(request):
    """KPIs completos para el dashboard principal"""
    total = Paciente.objects.count()
    etl_total = ETLHistory.objects.count()
    modelos_entrenados = MLModel.objects.count()

    if total == 0:
        return Response({
            'total_pacientes': 0,
            'etl_ejecutados': etl_total,
            'modelos_entrenados': modelos_entrenados,
            'message': 'Ejecute el proceso ETL para cargar datos',
        })

    qs = Paciente.objects.all()

    # Distribución de riesgo
    riesgo = dict(
        qs.values_list('riesgo_enfermedad')
        .annotate(c=Count('id'))
        .values_list('riesgo_enfermedad', 'c')
    )

    # Métricas del último modelo
    ultimo_modelo = MLModel.objects.first()
    ml_info = None
    if ultimo_modelo:
        ml_info = {
            'tipo': ultimo_modelo.model_type,
            'accuracy': ultimo_modelo.accuracy,
            'f1_score': ultimo_modelo.f1_score,
            'fecha': ultimo_modelo.fecha_entrenamiento.isoformat(),
        }

    # Último ETL
    ultimo_etl = ETLHistory.objects.order_by('-fecha_inicio').first()
    etl_info = None
    if ultimo_etl:
        etl_info = {
            'fecha': ultimo_etl.fecha_inicio.isoformat(),
            'estado': ultimo_etl.estado,
            'registros_cargados': ultimo_etl.registros_cargados,
            'tiempo': ultimo_etl.tiempo_ejecucion,
        }

    return Response({
        'total_pacientes': total,
        'pacientes_criticos': qs.filter(es_critico=True).count(),
        'pacientes_hipertensos': qs.filter(es_hipertenso=True).count(),
        'pacientes_diabeticos': qs.filter(es_diabetico=True).count(),
        'pacientes_fumadores': qs.filter(fumador=True).count(),
        'distribucion_riesgo': riesgo,
        'promedio_edad': round(qs.aggregate(v=Avg('edad'))['v'] or 0, 1),
        'promedio_imc': round(qs.aggregate(v=Avg('imc'))['v'] or 0, 2),
        'promedio_glucosa': round(qs.aggregate(v=Avg('glucosa'))['v'] or 0, 2),
        'etl_ejecutados': etl_total,
        'modelos_entrenados': modelos_entrenados,
        'ultimo_modelo': ml_info,
        'ultimo_etl': etl_info,
    })
