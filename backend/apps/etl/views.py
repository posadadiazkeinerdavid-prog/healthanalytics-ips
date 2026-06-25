"""
ETL Views - Ejecución ETL, subida CSV, gestión de pacientes
"""

import os
import tempfile
import threading
from django.conf import settings
from django.utils import timezone
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsAdminOrAnalista, IsAdministrador
from .models import Paciente, ETLHistory
from .serializers import PacienteSerializer, PacienteListSerializer, ETLHistorySerializer
from .services import ETLService

_etl_lock = threading.Lock()
_etl_running = False


# ─── PACIENTES ──────────────────────────────────────────────────────────────────

class PacienteListView(generics.ListAPIView):
    """Listado de pacientes con filtros y búsqueda"""
    serializer_class = PacienteListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombres', 'apellidos', 'diagnostico_preliminar', 'riesgo_enfermedad']
    ordering_fields = ['edad', 'imc', 'glucosa', 'presion_sistolica', 'fecha_consulta']
    ordering = ['-fecha_registro']

    def get_queryset(self):
        qs = Paciente.objects.all()
        riesgo = self.request.query_params.get('riesgo')
        sexo = self.request.query_params.get('sexo')
        critico = self.request.query_params.get('critico')
        diagnostico = self.request.query_params.get('diagnostico')

        if riesgo:
            qs = qs.filter(riesgo_enfermedad=riesgo)
        if sexo:
            qs = qs.filter(sexo=sexo.upper())
        if critico in ['true', '1']:
            qs = qs.filter(es_critico=True)
        if diagnostico:
            qs = qs.filter(diagnostico_preliminar__icontains=diagnostico)
        return qs


class PacienteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle completo de un paciente"""
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]
    queryset = Paciente.objects.all()


# ─── ETL ─────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAdminOrAnalista])
def run_etl_base_dataset(request):
    """
    Ejecuta ETL sobre el dataset base (Excel incluido en el proyecto)
    """
    global _etl_running
    if _etl_running:
        return Response(
            {'error': 'Ya hay un proceso ETL en ejecución. Espere a que finalice.'},
            status=status.HTTP_409_CONFLICT
        )

    base_path = os.path.join(settings.DATASETS_DIR, 'dataset_clinico_etl_1800_registros.xlsx')
    if not os.path.exists(base_path):
        return Response(
            {'error': 'Dataset base no encontrado. Coloca el archivo en /datasets/'},
            status=status.HTTP_404_NOT_FOUND
        )

    etl_record = ETLHistory.objects.create(
        usuario=request.user,
        fuente='DATASET_BASE',
        archivo_fuente='dataset_clinico_etl_1800_registros.xlsx',
        estado='EN_PROCESO',
    )

    try:
        _etl_running = True
        service = ETLService()
        result = service.run(base_path, source_type='DATASET_BASE', etl_record=etl_record)
    except Exception as e:
        etl_record.estado = 'ERROR'
        etl_record.mensaje_error = str(e)
        etl_record.fecha_fin = timezone.now()
        etl_record.save()
        return Response({
            'etl_id': etl_record.id,
            'status': 'ERROR',
            'error': str(e),
            'log': f'Error crítico durante el ETL: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        _etl_running = False
        etl_record.refresh_from_db()

    return Response({
        'etl_id': etl_record.id,
        **result
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminOrAnalista])
@parser_classes([MultiPartParser, FormParser])
def upload_and_run_etl(request):
    """
    Sube un archivo CSV/Excel y ejecuta ETL automáticamente
    """
    global _etl_running
    if _etl_running:
        return Response(
            {'error': 'Ya hay un proceso ETL en ejecución. Espere a que finalice.'},
            status=status.HTTP_409_CONFLICT
        )

    archivo = request.FILES.get('archivo')
    if not archivo:
        return Response(
            {'error': 'No se proporcionó archivo. Asegúrate de adjuntar el campo "archivo".'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validar tamaño (50 MB máx)
    if archivo.size > 50 * 1024 * 1024:
        return Response(
            {'error': 'Archivo demasiado grande. Máximo 50 MB.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in ['.csv', '.xlsx', '.xls']:
        return Response(
            {'error': f'Formato "{ext}" no soportado. Use CSV o Excel (.xlsx/.xls)'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Guardar archivo temporalmente
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            for chunk in archivo.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
    except Exception as e:
        return Response(
            {'error': f'Error guardando archivo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    etl_record = ETLHistory.objects.create(
        usuario=request.user,
        fuente='CSV_UPLOAD' if ext == '.csv' else 'EXCEL_UPLOAD',
        archivo_fuente=archivo.name,
        estado='EN_PROCESO',
    )

    try:
        _etl_running = True
        service = ETLService()
        result = service.run(
            tmp_path,
            source_type='CSV_UPLOAD' if ext == '.csv' else 'EXCEL_UPLOAD',
            etl_record=etl_record
        )
    except Exception as e:
        etl_record.estado = 'ERROR'
        etl_record.mensaje_error = str(e)
        etl_record.fecha_fin = timezone.now()
        etl_record.save()
        return Response({
            'etl_id': etl_record.id,
            'status': 'ERROR',
            'error': str(e),
            'log': f'Error crítico durante el ETL: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        _etl_running = False
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    etl_record.refresh_from_db()
    return Response({'etl_id': etl_record.id, **result}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def etl_history_list(request):
    """Historial de procesos ETL"""
    records = ETLHistory.objects.all().order_by('-fecha_inicio')[:50]
    serializer = ETLHistorySerializer(records, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def etl_history_detail(request, pk):
    """Detalle de un proceso ETL con log completo"""
    try:
        record = ETLHistory.objects.get(pk=pk)
    except ETLHistory.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ETLHistorySerializer(record)
    return Response(serializer.data)