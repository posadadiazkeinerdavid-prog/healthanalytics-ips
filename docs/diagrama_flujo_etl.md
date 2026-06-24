# Diagrama de Flujo ETL — HealthAnalytics IPS

## Pipeline ETL Completo

┌──────────────────────────────────────────────────────────────┐
│                    1. EXTRACT (Extracción)                    │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  Excel .xlsx │    │   CSV file   │    │ Dataset Base  │  │
│  │  (openpyxl)  │    │  (pandas)    │    │ 1800 registros│  │
│  └──────┬───────┘    └──────┬───────┘    └───────┬───────┘  │
│         └──────────────────┴────────────────────┘           │
│                              │                               │
│                    pandas DataFrame                          │
│                    Registro: fuente, tiempo, nº filas        │
└──────────────────────────────┬───────────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────────────┐
│                  2. TRANSFORM (Transformación)                │
│                                                              │
│  Paso 1 → Renombrar columnas                                 │
│    presión_sistólica   → presion_sistolica                   │
│    saturación_oxígeno  → saturacion_oxigeno                  │
│                                                              │
│  Paso 2 → Eliminar Duplicados                                │
│    subset=['id_paciente'], keep='first'                      │
│                                                              │
│  Paso 3 → Conversión de Tipos                                │
│    edad: "Treinta" → NaN → int                               │
│    presion_sistolica: "Alta" → NaN → int                     │
│    glucosa, colesterol → float                               │
│    fumador, antecedentes → bool                              │
│    fecha_consulta → date                                     │
│                                                              │
│  Paso 4 → Validación de Rangos Clínicos                      │
│    edad: (0–120)         peso: (2–300 kg)                    │
│    altura: (0.3–2.5 m)   glucosa: (50–600)                   │
│    presión sistólica: (60–250)                               │
│    temperatura: (30–43 °C)                                   │
│    Fuera de rango → NaN                                      │
│                                                              │
│  Paso 5 → Tratamiento de Nulos                               │
│    Numéricos (peso, glucosa...)  → Media                     │
│    Enteros (edad, presión...)    → Mediana                   │
│    Saturación O₂                → 97.0 (valor normal)       │
│    Categóricos (sexo, diagnóst.) → Moda                      │
│    Booleanos                    → False                      │
│    fecha_consulta               → Fecha actual               │
│                                                              │
│  Paso 6 → Normalización de Categóricos                       │
│    "masculino", "male", "hombre" → "M"                       │
│    "hipertencion", "hipertensíon" → "Hipertensión"           │
│    "moderada", "muy alta" → estandarizado                    │
│                                                              │
│  Paso 7 → Cálculo de IMC                                     │
│    IMC = peso / altura²                                      │
│    < 18.5      → Bajo peso                                   │
│    18.5 – 24.9 → Normal                                      │
│    25 – 29.9   → Sobrepeso                                   │
│    >= 30       → Obesidad                                    │
│                                                              │
│  Paso 8 → Clasificación de Riesgo                            │
│    Crítico: presión_s > 180 OR glucosa > 300                 │
│             OR saturación < 85                               │
│    Alto:    presión_s >= 160 OR glucosa >= 200               │
│             OR IMC >= 35                                     │
│    Medio:   presión_s >= 140 OR glucosa >= 126               │
│             OR IMC >= 30 OR colesterol >= 240                │
│    Bajo:    resto de casos                                   │
└──────────────────────────────┬───────────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────────────┐
│                      3. LOAD (Carga)                         │
│                                                              │
│  Comparar id_paciente con registros existentes en BD         │
│    Nuevo      → bulk_create (batch = 200)                    │
│    Existente  → UPDATE campos clínicos                       │
│                                                              │
│  Guardar en etl_history:                                     │
│    · fecha_inicio / fecha_fin                                │
│    · registros_extraidos, duplicados, invalidos              │
│    · registros_cargados                                      │
│    · tiempo_ejecucion (segundos)                             │
│    · estado: COMPLETADO / ERROR                              │
│    · log_detalle (línea por línea)                           │
└──────────────────────────────────────────────────────────────┘

## Estados del proceso ETL

[PENDIENTE] → [EN_PROCESO] → [COMPLETADO]
↘ [ERROR]

## Estadísticas que genera el ETL

| Campo                    | Descripción                            |
|--------------------------|----------------------------------------|
| registros_extraidos      | Total de filas leídas del archivo      |
| registros_duplicados     | Filas eliminadas por id_paciente dup.  |
| registros_invalidos      | Valores fuera de rango clínico         |
| registros_nulos_tratados | Celdas vacías imputadas                |
| registros_cargados       | Filas insertadas/actualizadas en BD    |
| tiempo_ejecucion         | Duración total en segundos             |