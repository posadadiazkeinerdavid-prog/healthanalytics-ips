# ERD — Modelo Relacional HealthAnalytics IPS

## Tablas y Campos

┌─────────────────────────────────────┐
│            auth_users               │
├─────────────────────────────────────┤
│ PK  id               INT            │
│     email            VARCHAR(254) UQ│
│     nombres          VARCHAR(100)   │
│     apellidos        VARCHAR(100)   │
│     role             VARCHAR(20)    │
│     [administrador | medico |       │
│      analista]                      │
│     password         VARCHAR(128)   │
│     is_active        BOOLEAN        │
│     is_staff         BOOLEAN        │
│     date_joined      DATETIME       │
└──────────────┬──────────────────────┘
│ 1
│
│ N
┌──────────────▼──────────────────────┐
│            etl_history              │
├─────────────────────────────────────┤
│ PK  id                  INT         │
│ FK  usuario_id          INT         │
│     fecha_inicio        DATETIME    │
│     fecha_fin           DATETIME    │
│     tiempo_ejecucion    FLOAT       │
│     fuente              VARCHAR(20) │
│     [DATASET_BASE | CSV_UPLOAD |    │
│      EXCEL_UPLOAD | GENERADO]       │
│     archivo_fuente      VARCHAR(255)│
│     registros_extraidos INT         │
│     registros_duplicados INT        │
│     registros_nulos     INT         │
│     registros_invalidos INT         │
│     registros_cargados  INT         │
│     estado              VARCHAR(20) │
│     [PENDIENTE | EN_PROCESO |       │
│      COMPLETADO | ERROR]            │
│     log_detalle         TEXT        │
│     mensaje_error       TEXT        │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│              pacientes              │
├─────────────────────────────────────┤
│ PK  id                  INT         │
│     id_paciente         INT  UQ     │
│                                     │
│  -- Identificación --               │
│     nombres             VARCHAR(100)│
│     apellidos           VARCHAR(100)│
│                                     │
│  -- Demografía --                   │
│     edad                INT         │
│     sexo                VARCHAR(1)  │
│     [M | F]                         │
│                                     │
│  -- Antropometría --                │
│     peso                FLOAT       │
│     altura              FLOAT       │
│     imc                 FLOAT       │
│     imc_clasificacion   VARCHAR(20) │
│     [Bajo peso | Normal |           │
│      Sobrepeso | Obesidad]          │
│                                     │
│  -- Signos Vitales --               │
│     presion_sistolica   INT         │
│     presion_diastolica  INT         │
│     frecuencia_cardiaca INT         │
│     glucosa             FLOAT       │
│     colesterol          FLOAT       │
│     saturacion_oxigeno  FLOAT       │
│     temperatura         FLOAT       │
│                                     │
│  -- Factores de Riesgo --           │
│     antecedentes_familiares BOOLEAN │
│     fumador             BOOLEAN     │
│     consumo_alcohol     BOOLEAN     │
│     actividad_fisica    VARCHAR(20) │
│     [Sedentario | Baja |            │
│      Media | Alta]                  │
│                                     │
│  -- Diagnóstico --                  │
│     diagnostico_preliminar          │
│          VARCHAR(100)               │
│     riesgo_enfermedad   VARCHAR(20) │
│     [Bajo | Medio | Alto | Crítico] │
│                                     │
│  -- Timestamps --                   │
│     fecha_consulta      DATE        │
│     fecha_registro      DATETIME    │
│     fecha_actualizacion DATETIME    │
│                                     │
│  -- Flags Calculados --             │
│     es_critico          BOOLEAN     │
│     es_hipertenso       BOOLEAN     │
│     es_diabetico        BOOLEAN     │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│             ml_models               │
├─────────────────────────────────────┤
│ PK  id                  INT         │
│ FK  usuario_id          INT         │
│     model_type          VARCHAR(30) │
│     [random_forest |                │
│      logistic_regression |          │
│      decision_tree]                 │
│     fecha_entrenamiento DATETIME    │
│     accuracy            FLOAT       │
│     precision           FLOAT       │
│     recall              FLOAT       │
│     f1_score            FLOAT       │
│     total_samples       INT         │
│     train_samples       INT         │
│     test_samples        INT         │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│           ml_predictions            │
├─────────────────────────────────────┤
│ PK  id                  INT         │
│ FK  usuario_id          INT         │
│     fecha               DATETIME    │
│     datos_entrada       JSON        │
│     riesgo_predicho     VARCHAR(20) │
│     confianza           FLOAT       │
│     probabilidades      JSON        │
│     modelo_usado        VARCHAR(30) │
└─────────────────────────────────────┘

## Relaciones

| Tabla origen    | Relación | Tabla destino | Descripción                         |
|-----------------|----------|---------------|-------------------------------------|
| etl_history     | N → 1    | auth_users    | Un usuario ejecuta muchos ETLs      |
| ml_models       | N → 1    | auth_users    | Un usuario entrena muchos modelos   |
| ml_predictions  | N → 1    | auth_users    | Un usuario hace muchas predicciones |

## Índices definidos en pacientes

| Campo                  | Tipo   | Motivo                             |
|------------------------|--------|------------------------------------|
| id_paciente            | UNIQUE | Clave de negocio, evita duplicados |
| riesgo_enfermedad      | INDEX  | Filtros frecuentes por riesgo      |
| diagnostico_preliminar | INDEX  | Segmentación por diagnóstico       |
| es_critico             | INDEX  | Dashboard de pacientes críticos    |

