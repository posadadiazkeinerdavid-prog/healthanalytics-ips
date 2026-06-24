from django.urls import path
from .views import (
    kpis_view, estadistica_descriptiva_view, segmentacion_riesgo_view,
    segmentacion_sexo_view, segmentacion_diagnostico_view, segmentacion_imc_view,
    pacientes_criticos_view, tendencia_edad_riesgo_view, heatmap_correlacion_view,
    top_pacientes_categoria_view
)
urlpatterns = [
    path('kpis/', kpis_view, name='analytics-kpis'),
    path('estadisticas/', estadistica_descriptiva_view, name='analytics-estadisticas'),
    path('segmentacion/riesgo/', segmentacion_riesgo_view),
    path('segmentacion/sexo/', segmentacion_sexo_view),
    path('segmentacion/diagnostico/', segmentacion_diagnostico_view),
    path('segmentacion/imc/', segmentacion_imc_view),
    path('pacientes-criticos/', pacientes_criticos_view),
    path('tendencia-edad/', tendencia_edad_riesgo_view),
    path('heatmap/', heatmap_correlacion_view, name='analytics-heatmap'),
    path('top-pacientes/', top_pacientes_categoria_view, name='analytics-top-pacientes'),
]