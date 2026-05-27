# Diagrama de Arquitectura — HealthAnalytics IPS

## Arquitectura General del Sistema

┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE / BROWSER                        │
│                  HTML5 + Bootstrap 5 + Chart.js                 │
└──────────────────────────────┬──────────────────────────────────┘
│  HTTP / REST
▼
┌─────────────────────────────────────────────────────────────────┐
│                     DJANGO BACKEND (Python 3.14)                │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐  │
│  │    auth/    │  │    etl/     │  │      analytics/        │  │
│  │  JWT Login  │  │  ETL Engine │  │  KPIs · Estadísticas   │  │
│  │  Roles:     │  │  Extract    │  │  Segmentación          │  │
│  │  Admin      │  │  Transform  │  │  Detección Críticos    │  │
│  │  Médico     │  │  Load       │  └────────────────────────┘  │
│  │  Analista   │  └─────────────┘                              │
│  └─────────────┘                                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐  │
│  │     ml/     │  │  dashboard/ │  │       reports/         │  │
│  │ RandomForest│  │  KPI API    │  │  Export PDF            │  │
│  │ LogisticReg │  │  Gráficas   │  │  Export Excel          │  │
│  │ DecisionTree│  │  Frontend   │  │  Export CSV            │  │
│  └─────────────┘  └─────────────┘  └────────────────────────┘  │
│                                                                 │
│              Django REST Framework + drf-yasg (Swagger)        │
└──────────────────────────────┬──────────────────────────────────┘
│  ORM / SQL
▼
┌─────────────────────────────────────────────────────────────────┐
│                        MySQL 8.0                                │
│                                                                 │
│   auth_users │ pacientes │ etl_history │ ml_models              │
│              │           │             │ ml_predictions         │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHIVOS / STORAGE                           │
│   datasets/  ←  CSV / Excel de entrada                         │
│   ml_models/ ←  Modelos entrenados (.joblib)                   │
│   logs/      ←  Logs ETL y sistema                             │
└─────────────────────────────────────────────────────────────────┘