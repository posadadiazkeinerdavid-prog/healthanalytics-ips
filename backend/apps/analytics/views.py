"""
Analytics Views - Estadísticas clínicas, KPIs, segmentación
"""

from django.db.models import Count, Avg, Min, Max, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.etl.models import Paciente
import numpy as np


def _get_pacientes_qs():
    return Paciente.objects.all()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpis_view(request):
    qs = _get_pacientes_qs()
    total = qs.count()
    if total == 0:
        return Response({'total': 0, 'message': 'Sin datos. Ejecute el proceso ETL primero.'})

    criticos = qs.filter(es_critico=True).count()
    hipertensos = qs.filter(es_hipertenso=True).count()
    diabeticos = qs.filter(es_diabetico=True).count()
    fumadores = qs.filter(fumador=True).count()
    riesgo_counts = dict(qs.values_list('riesgo_enfermedad').annotate(c=Count('id')).values_list('riesgo_enfermedad', 'c'))
    edad_avg = qs.aggregate(v=Avg('edad'))['v'] or 0
    imc_avg = qs.aggregate(v=Avg('imc'))['v'] or 0
    glucosa_avg = qs.aggregate(v=Avg('glucosa'))['v'] or 0
    presion_s_avg = qs.aggregate(v=Avg('presion_sistolica'))['v'] or 0

    return Response({
        'total_pacientes': total,
        'pacientes_criticos': criticos,
        'pacientes_hipertensos': hipertensos,
        'pacientes_diabeticos': diabeticos,
        'pacientes_fumadores': fumadores,
        'distribucion_riesgo': riesgo_counts,
        'promedio_edad': round(edad_avg, 1),
        'promedio_imc': round(imc_avg, 2),
        'promedio_glucosa': round(glucosa_avg, 2),
        'promedio_presion_sistolica': round(presion_s_avg, 1),
        'porcentaje_criticos': round(criticos / total * 100, 1) if total else 0,
        'porcentaje_hipertensos': round(hipertensos / total * 100, 1) if total else 0,
        'porcentaje_diabeticos': round(diabeticos / total * 100, 1) if total else 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadistica_descriptiva_view(request):
    qs = _get_pacientes_qs()
    if not qs.exists():
        return Response({'message': 'Sin datos'})

    fields = ['edad', 'peso', 'altura', 'imc', 'presion_sistolica',
              'presion_diastolica', 'frecuencia_cardiaca', 'glucosa',
              'colesterol', 'saturacion_oxigeno', 'temperatura']

    result = {}
    for field in fields:
        vals = [v for v in qs.values_list(field, flat=True) if v is not None]
        if vals:
            arr = np.array(vals)
            from scipy import stats as sp_stats
            mode_result = sp_stats.mode(arr, keepdims=True)
            result[field] = {
                'media': round(float(np.mean(arr)), 2),
                'mediana': round(float(np.median(arr)), 2),
                'moda': round(float(mode_result.mode[0]), 2),
                'desviacion_std': round(float(np.std(arr)), 2),
                'minimo': round(float(np.min(arr)), 2),
                'maximo': round(float(np.max(arr)), 2),
                'n': len(vals),
            }
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def segmentacion_riesgo_view(request):
    qs = _get_pacientes_qs()
    data = (qs.values('riesgo_enfermedad')
              .annotate(total=Count('id'), edad_promedio=Avg('edad'),
                        imc_promedio=Avg('imc'), glucosa_promedio=Avg('glucosa'))
              .order_by('riesgo_enfermedad'))
    return Response(list(data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def segmentacion_sexo_view(request):
    qs = _get_pacientes_qs()
    data = (qs.values('sexo')
              .annotate(total=Count('id'),
                        criticos=Count('id', filter=Q(es_critico=True)),
                        hipertensos=Count('id', filter=Q(es_hipertenso=True)),
                        diabeticos=Count('id', filter=Q(es_diabetico=True)),
                        imc_promedio=Avg('imc')))
    return Response(list(data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def segmentacion_diagnostico_view(request):
    qs = _get_pacientes_qs()
    data = (qs.values('diagnostico_preliminar')
              .annotate(total=Count('id'), edad_promedio=Avg('edad'),
                        riesgo_alto=Count('id', filter=Q(riesgo_enfermedad__in=['Alto', 'Crítico'])))
              .order_by('-total'))
    return Response(list(data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def segmentacion_imc_view(request):
    qs = _get_pacientes_qs()
    data = (qs.values('imc_clasificacion')
              .annotate(total=Count('id'), glucosa_promedio=Avg('glucosa'),
                        presion_promedio=Avg('presion_sistolica'),
                        criticos=Count('id', filter=Q(es_critico=True)))
              .order_by('-total'))
    return Response(list(data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pacientes_criticos_view(request):
    criticos = _get_pacientes_qs().filter(es_critico=True).order_by('-presion_sistolica')[:100]
    data = list(criticos.values(
        'id_paciente', 'nombres', 'apellidos', 'edad', 'sexo',
        'presion_sistolica', 'glucosa', 'saturacion_oxigeno',
        'riesgo_enfermedad', 'diagnostico_preliminar'
    ))
    return Response({'total': len(data), 'pacientes': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tendencia_edad_riesgo_view(request):
    qs = _get_pacientes_qs()
    grupos = [
        ('0-17', 0, 17), ('18-35', 18, 35), ('36-50', 36, 50),
        ('51-65', 51, 65), ('66-80', 66, 80), ('80+', 81, 150),
    ]
    result = []
    for label, lo, hi in grupos:
        g = qs.filter(edad__gte=lo, edad__lte=hi)
        total = g.count()
        if total == 0:
            continue
        result.append({
            'grupo_edad': label, 'total': total,
            'bajo':    g.filter(riesgo_enfermedad='Bajo').count(),
            'medio':   g.filter(riesgo_enfermedad='Medio').count(),
            'alto':    g.filter(riesgo_enfermedad='Alto').count(),
            'critico': g.filter(riesgo_enfermedad='Crítico').count(),
            'imc_promedio': round(g.aggregate(v=Avg('imc'))['v'] or 0, 2),
        })
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def heatmap_correlacion_view(request):
    qs = _get_pacientes_qs()
    if not qs.exists():
        return Response({'message': 'Sin datos'})

    fields = ['edad', 'imc', 'glucosa', 'colesterol',
              'presion_sistolica', 'frecuencia_cardiaca', 'saturacion_oxigeno']
    labels = ['Edad', 'IMC', 'Glucosa', 'Colesterol',
              'Presión S.', 'Frec. Card.', 'Saturación O₂']

    import pandas as pd
    vals = list(qs.values(*fields))
    if not vals:
        return Response({'message': 'Sin datos'})

    df = pd.DataFrame(vals).dropna()
    corr = df.corr().round(3)
    matrix = []
    for i, row_label in enumerate(labels):
        for j, col_label in enumerate(labels):
            matrix.append({'x': col_label, 'y': row_label, 'v': float(corr.iloc[i, j])})
    return Response({'labels': labels, 'matrix': matrix})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_pacientes_categoria_view(request):
    """Top 10 pacientes por categoría para modal del dashboard"""
    categoria = request.GET.get('categoria', 'criticos')
    limit = int(request.GET.get('limit', 10))
    qs = _get_pacientes_qs()

    campos = ['id_paciente', 'nombres', 'apellidos', 'edad', 'sexo',
              'presion_sistolica', 'glucosa', 'saturacion_oxigeno',
              'imc', 'colesterol', 'frecuencia_cardiaca',
              'riesgo_enfermedad', 'diagnostico_preliminar', 'fumador']

    config = {
        'criticos':    {'filter': Q(es_critico=True),    'order': '-presion_sistolica', 'label': 'Pacientes Críticos',    'color': '#ef4444'},
        'hipertensos': {'filter': Q(es_hipertenso=True), 'order': '-presion_sistolica', 'label': 'Pacientes Hipertensos', 'color': '#fb923c'},
        'diabeticos':  {'filter': Q(es_diabetico=True),  'order': '-glucosa',           'label': 'Pacientes Diabéticos',  'color': '#c084fc'},
        'fumadores':   {'filter': Q(fumador=True),        'order': '-edad',              'label': 'Pacientes Fumadores',   'color': '#22d3ee'},
        'alto_riesgo': {'filter': Q(riesgo_enfermedad__in=['Alto', 'Crítico']), 'order': '-presion_sistolica', 'label': 'Alto Riesgo', 'color': '#fbbf24'},
        'todos':       {'filter': Q(),                    'order': '-presion_sistolica', 'label': 'Todos los Pacientes',   'color': '#60a5fa'},
    }

    cfg = config.get(categoria, config['criticos'])
    pacientes = list(qs.filter(cfg['filter']).order_by(cfg['order'])[:limit].values(*campos))

    return Response({
        'categoria': categoria,
        'label': cfg['label'],
        'color': cfg['color'],
        'total': qs.filter(cfg['filter']).count(),
        'pacientes': pacientes,
    })