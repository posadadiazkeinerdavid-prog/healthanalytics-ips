from django.urls import path
from .views import export_csv, export_excel, export_pdf, reporte_summary

urlpatterns = [
    path('', reporte_summary, name='reporte-summary'),
    path('csv/', export_csv, name='export-csv'),
    path('excel/', export_excel, name='export-excel'),
    path('pdf/', export_pdf, name='export-pdf'),
]
