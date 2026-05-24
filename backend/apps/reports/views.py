"""
Reports Views - Exportación de reportes en PDF, Excel y CSV
"""

import io
import csv
import json
from datetime import datetime

from django.http import HttpResponse
from django.db.models import Count, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.etl.models import Paciente, ETLHistory
from apps.ml.models import MLModel


def _get_filename(prefix, ext):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{ts}.{ext}'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_csv(request):
    """Exporta pacientes a CSV"""
    qs = Paciente.objects.all().order_by('id_paciente')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{_get_filename("pacientes", "csv")}"'
    response.write('\ufeff')  # BOM para Excel

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nombres', 'Apellidos', 'Edad', 'Sexo', 'Peso', 'Altura', 'IMC',
        'Clasif IMC', 'P.Sistólica', 'P.Diastólica', 'Frec.Cardiaca',
        'Glucosa', 'Colesterol', 'Sat.O2', 'Temperatura',
        'Ant.Familiares', 'Fumador', 'Alcohol', 'Actividad',
        'Diagnóstico', 'Riesgo', 'Fecha Consulta', 'Es Crítico'
    ])
    for p in qs:
        writer.writerow([
            p.id_paciente, p.nombres, p.apellidos, p.edad, p.sexo,
            p.peso, p.altura, p.imc, p.imc_clasificacion,
            p.presion_sistolica, p.presion_diastolica, p.frecuencia_cardiaca,
            p.glucosa, p.colesterol, p.saturacion_oxigeno, p.temperatura,
            p.antecedentes_familiares, p.fumador, p.consumo_alcohol, p.actividad_fisica,
            p.diagnostico_preliminar, p.riesgo_enfermedad, p.fecha_consulta, p.es_critico
        ])
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_excel(request):
    """Exporta pacientes a Excel"""
    import xlsxwriter

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # ── Hoja Pacientes ──
    ws = workbook.add_worksheet('Pacientes')
    header_fmt = workbook.add_format({
        'bold': True, 'bg_color': '#0d6efd', 'font_color': 'white',
        'border': 1, 'align': 'center'
    })
    critico_fmt = workbook.add_format({'bg_color': '#f8d7da'})

    headers = [
        'ID', 'Nombres', 'Apellidos', 'Edad', 'Sexo', 'Peso', 'Altura', 'IMC',
        'Clasif IMC', 'P.Sistólica', 'P.Diastólica', 'Frec.Cardíaca',
        'Glucosa', 'Colesterol', 'Sat.O₂', 'Temperatura',
        'Ant.Familiares', 'Fumador', 'Alcohol', 'Actividad',
        'Diagnóstico', 'Riesgo', 'Fecha Consulta', 'Crítico'
    ]
    for col, h in enumerate(headers):
        ws.write(0, col, h, header_fmt)
    ws.set_column(0, len(headers), 15)

    qs = Paciente.objects.all().order_by('id_paciente')
    for row, p in enumerate(qs, start=1):
        fmt = critico_fmt if p.es_critico else None
        data = [
            p.id_paciente, p.nombres, p.apellidos, p.edad, p.sexo,
            p.peso, p.altura, p.imc or 0, p.imc_clasificacion or '',
            p.presion_sistolica, p.presion_diastolica, p.frecuencia_cardiaca,
            p.glucosa, p.colesterol, p.saturacion_oxigeno, p.temperatura,
            str(p.antecedentes_familiares), str(p.fumador), str(p.consumo_alcohol),
            p.actividad_fisica, p.diagnostico_preliminar, p.riesgo_enfermedad,
            str(p.fecha_consulta), str(p.es_critico)
        ]
        for col, val in enumerate(data):
            ws.write(row, col, val, fmt)

    # ── Hoja KPIs ──
    ws2 = workbook.add_worksheet('KPIs')
    title_fmt = workbook.add_format({'bold': True, 'font_size': 14})
    ws2.write(0, 0, 'HealthAnalytics IPS - Resumen Ejecutivo', title_fmt)
    ws2.write(1, 0, f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}')

    total = Paciente.objects.count()
    kpis = [
        ('Total Pacientes', total),
        ('Pacientes Críticos', Paciente.objects.filter(es_critico=True).count()),
        ('Pacientes Hipertensos', Paciente.objects.filter(es_hipertenso=True).count()),
        ('Pacientes Diabéticos', Paciente.objects.filter(es_diabetico=True).count()),
        ('Pacientes Fumadores', Paciente.objects.filter(fumador=True).count()),
        ('Promedio Edad', round(Paciente.objects.aggregate(v=Avg('edad'))['v'] or 0, 1)),
        ('Promedio IMC', round(Paciente.objects.aggregate(v=Avg('imc'))['v'] or 0, 2)),
        ('Promedio Glucosa', round(Paciente.objects.aggregate(v=Avg('glucosa'))['v'] or 0, 2)),
    ]
    for r, (k, v) in enumerate(kpis, start=3):
        ws2.write(r, 0, k)
        ws2.write(r, 1, v)

    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{_get_filename("reporte", "xlsx")}"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pdf(request):
    """Exporta reporte ejecutivo a PDF"""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, HRFlowable
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('title', parent=styles['Title'],
                                  fontSize=18, textColor=colors.HexColor('#0d6efd'))
    subtitle_style = ParagraphStyle('subtitle', parent=styles['Normal'],
                                     fontSize=10, textColor=colors.gray)
    section_style = ParagraphStyle('section', parent=styles['Heading2'],
                                    fontSize=12, textColor=colors.HexColor('#0d6efd'),
                                    spaceAfter=6)

    # Header
    story.append(Paragraph('HealthAnalytics IPS', title_style))
    story.append(Paragraph('Reporte Ejecutivo de Analítica Clínica', subtitle_style))
    story.append(Paragraph(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', subtitle_style))
    story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#0d6efd')))
    story.append(Spacer(1, 0.5*cm))

    # KPIs
    story.append(Paragraph('Indicadores Clave (KPIs)', section_style))
    total = Paciente.objects.count()
    criticos = Paciente.objects.filter(es_critico=True).count()
    hipert = Paciente.objects.filter(es_hipertenso=True).count()
    diab = Paciente.objects.filter(es_diabetico=True).count()
    fumad = Paciente.objects.filter(fumador=True).count()

    kpi_data = [
        ['Indicador', 'Valor', 'Porcentaje'],
        ['Total Pacientes', str(total), '100%'],
        ['Pacientes Críticos', str(criticos), f'{criticos/total*100:.1f}%' if total else '0%'],
        ['Hipertensos', str(hipert), f'{hipert/total*100:.1f}%' if total else '0%'],
        ['Diabéticos', str(diab), f'{diab/total*100:.1f}%' if total else '0%'],
        ['Fumadores', str(fumad), f'{fumad/total*100:.1f}%' if total else '0%'],
    ]
    t = Table(kpi_data, colWidths=[8*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Distribución por riesgo
    story.append(Paragraph('Distribución por Nivel de Riesgo', section_style))
    riesgo_data = list(
        Paciente.objects.values('riesgo_enfermedad')
        .annotate(total=Count('id'))
        .order_by('riesgo_enfermedad')
    )
    risk_table_data = [['Riesgo', 'Total', 'Porcentaje']]
    risk_colors = {'Bajo': '#198754', 'Medio': '#ffc107', 'Alto': '#fd7e14', 'Crítico': '#dc3545'}
    for r in riesgo_data:
        pct = f'{r["total"]/total*100:.1f}%' if total else '0%'
        risk_table_data.append([r['riesgo_enfermedad'], str(r['total']), pct])
    rt = Table(risk_table_data, colWidths=[8*cm, 4*cm, 4*cm])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(rt)
    story.append(Spacer(1, 0.5*cm))

    # ETL History
    story.append(Paragraph('Historial ETL Reciente', section_style))
    etl_qs = ETLHistory.objects.order_by('-fecha_inicio')[:10]
    etl_data = [['Fecha', 'Fuente', 'Estado', 'Registros', 'Tiempo (s)']]
    for e in etl_qs:
        etl_data.append([
            e.fecha_inicio.strftime('%d/%m/%Y %H:%M'),
            e.fuente, e.estado,
            str(e.registros_cargados),
            str(round(e.tiempo_ejecucion or 0, 1))
        ])
    et = Table(etl_data, colWidths=[4*cm, 3.5*cm, 2.5*cm, 2.5*cm, 3*cm])
    et.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    story.append(et)

    # ML
    ultimo_ml = MLModel.objects.first()
    if ultimo_ml:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph('Métricas Machine Learning', section_style))
        ml_data = [
            ['Modelo', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'Muestras'],
            [
                ultimo_ml.model_type, f'{ultimo_ml.accuracy:.4f}',
                f'{ultimo_ml.precision:.4f}', f'{ultimo_ml.recall:.4f}',
                f'{ultimo_ml.f1_score:.4f}', str(ultimo_ml.total_samples)
            ]
        ]
        mt = Table(ml_data, colWidths=[3.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        mt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6f42c1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(mt)

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{_get_filename("reporte_clinico", "pdf")}"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_summary(request):
    """Resumen para el módulo de reportes"""
    total = Paciente.objects.count()
    return Response({
        'total_pacientes': total,
        'etl_ejecutados': ETLHistory.objects.count(),
        'modelos_entrenados': MLModel.objects.count(),
        'ultimo_etl': ETLHistory.objects.values('fecha_inicio', 'estado', 'registros_cargados').first(),
    })
