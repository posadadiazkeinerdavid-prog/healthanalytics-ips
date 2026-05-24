"""
ETL Models - Paciente y Historial ETL
"""

from django.db import models
from django.conf import settings


class Paciente(models.Model):
    """Modelo principal de datos clínicos del paciente"""

    SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino')]
    ACTIVIDAD_CHOICES = [
        ('Sedentario', 'Sedentario'),
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]
    RIESGO_CHOICES = [
        ('Bajo', 'Bajo'),
        ('Medio', 'Medio'),
        ('Alto', 'Alto'),
        ('Crítico', 'Crítico'),
    ]
    IMC_CLASIFICACION_CHOICES = [
        ('Bajo peso', 'Bajo peso'),
        ('Normal', 'Normal'),
        ('Sobrepeso', 'Sobrepeso'),
        ('Obesidad', 'Obesidad'),
    ]
    DIAGNOSTICO_CHOICES = [
        ('Paciente sano', 'Paciente sano'),
        ('Prehipertensión', 'Prehipertensión'),
        ('Hipertensión', 'Hipertensión'),
        ('Diabetes Tipo 2', 'Diabetes Tipo 2'),
        ('Obesidad', 'Obesidad'),
        ('Riesgo cardiovascular', 'Riesgo cardiovascular'),
        ('Cardiopatía', 'Cardiopatía'),
    ]

    # Identificación
    id_paciente = models.IntegerField(unique=True, verbose_name='ID Paciente')
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')

    # Datos demográficos
    edad = models.IntegerField(verbose_name='Edad')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name='Sexo')

    # Medidas antropométricas
    peso = models.FloatField(verbose_name='Peso (kg)')
    altura = models.FloatField(verbose_name='Altura (m)')
    imc = models.FloatField(verbose_name='IMC', null=True, blank=True)
    imc_clasificacion = models.CharField(
        max_length=20, choices=IMC_CLASIFICACION_CHOICES,
        null=True, blank=True, verbose_name='Clasificación IMC'
    )

    # Signos vitales
    presion_sistolica = models.IntegerField(verbose_name='Presión Sistólica')
    presion_diastolica = models.IntegerField(verbose_name='Presión Diastólica')
    frecuencia_cardiaca = models.IntegerField(verbose_name='Frecuencia Cardíaca')
    glucosa = models.FloatField(verbose_name='Glucosa')
    colesterol = models.FloatField(verbose_name='Colesterol')
    saturacion_oxigeno = models.FloatField(verbose_name='Saturación O₂')
    temperatura = models.FloatField(verbose_name='Temperatura')

    # Factores de riesgo
    antecedentes_familiares = models.BooleanField(default=False, verbose_name='Antecedentes Familiares')
    fumador = models.BooleanField(default=False, verbose_name='Fumador')
    consumo_alcohol = models.BooleanField(default=False, verbose_name='Consumo Alcohol')
    actividad_fisica = models.CharField(
        max_length=20, choices=ACTIVIDAD_CHOICES, verbose_name='Actividad Física'
    )

    # Diagnóstico y riesgo
    diagnostico_preliminar = models.CharField(
        max_length=100, choices=DIAGNOSTICO_CHOICES, verbose_name='Diagnóstico Preliminar'
    )
    riesgo_enfermedad = models.CharField(
        max_length=20, choices=RIESGO_CHOICES, verbose_name='Riesgo de Enfermedad'
    )

    # Timestamps
    fecha_consulta = models.DateField(verbose_name='Fecha Consulta')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Registro')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')

    # Flags clínicos calculados
    es_critico = models.BooleanField(default=False, verbose_name='Es Crítico')
    es_hipertenso = models.BooleanField(default=False, verbose_name='Es Hipertenso')
    es_diabetico = models.BooleanField(default=False, verbose_name='Es Diabético')

    class Meta:
        db_table = 'pacientes'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['riesgo_enfermedad']),
            models.Index(fields=['diagnostico_preliminar']),
            models.Index(fields=['es_critico']),
        ]

    def __str__(self):
        return f'{self.nombres} {self.apellidos} - {self.riesgo_enfermedad}'

    def calcular_imc(self):
        if self.peso and self.altura and self.altura > 0:
            return round(self.peso / (self.altura ** 2), 2)
        return None

    def clasificar_imc(self):
        if self.imc is None:
            return None
        if self.imc < 18.5:
            return 'Bajo peso'
        elif self.imc <= 24.9:
            return 'Normal'
        elif self.imc <= 29.9:
            return 'Sobrepeso'
        else:
            return 'Obesidad'

    def detectar_critico(self):
        return (
            self.presion_sistolica > 180 or
            self.glucosa > 300 or
            self.saturacion_oxigeno < 85
        )

    def detectar_hipertenso(self):
        return self.presion_sistolica >= 140 or self.presion_diastolica >= 90

    def detectar_diabetico(self):
        return self.glucosa >= 126

    def save(self, *args, **kwargs):
        self.imc = self.calcular_imc()
        self.imc_clasificacion = self.clasificar_imc()
        self.es_critico = self.detectar_critico()
        self.es_hipertenso = self.detectar_hipertenso()
        self.es_diabetico = self.detectar_diabetico()
        super().save(*args, **kwargs)


class ETLHistory(models.Model):
    """Registro histórico de procesos ETL ejecutados"""

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
    ]

    FUENTE_CHOICES = [
        ('DATASET_BASE', 'Dataset Base'),
        ('CSV_UPLOAD', 'CSV Subido'),
        ('EXCEL_UPLOAD', 'Excel Subido'),
        ('GENERADO', 'Generado Automáticamente'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='etl_processes', verbose_name='Usuario'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Inicio')
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name='Fecha Fin')
    tiempo_ejecucion = models.FloatField(null=True, blank=True, verbose_name='Tiempo Ejecución (seg)')

    fuente = models.CharField(max_length=20, choices=FUENTE_CHOICES, verbose_name='Fuente')
    archivo_fuente = models.CharField(max_length=255, null=True, blank=True, verbose_name='Archivo Fuente')

    registros_extraidos = models.IntegerField(default=0, verbose_name='Registros Extraídos')
    registros_duplicados = models.IntegerField(default=0, verbose_name='Registros Duplicados')
    registros_nulos = models.IntegerField(default=0, verbose_name='Registros con Nulos')
    registros_invalidos = models.IntegerField(default=0, verbose_name='Registros Inválidos')
    registros_cargados = models.IntegerField(default=0, verbose_name='Registros Cargados')

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    log_detalle = models.TextField(blank=True, verbose_name='Log Detallado')
    mensaje_error = models.TextField(blank=True, verbose_name='Mensaje Error')

    class Meta:
        db_table = 'etl_history'
        verbose_name = 'Historial ETL'
        verbose_name_plural = 'Historial ETL'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'ETL #{self.pk} - {self.estado} - {self.fecha_inicio.strftime("%Y-%m-%d %H:%M")}'
