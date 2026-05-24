# 🏥 HealthAnalytics IPS

**Plataforma Inteligente de Analítica Clínica para Detección de Riesgo Médico**

![Stack](https://img.shields.io/badge/Python-3.12-blue) ![Django](https://img.shields.io/badge/Django-4.2-green) ![MySQL](https://img.shields.io/badge/MySQL-8.0-orange) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple) ![ML](https://img.shields.io/badge/Scikit--Learn-1.5-red)

---

## 📋 Descripción General

HealthAnalytics IPS es una plataforma web FullStack que automatiza el procesamiento de datos clínicos mediante un pipeline **ETL completo**, **analítica estadística** y **modelos de Machine Learning** para predecir riesgo de enfermedades y detectar pacientes críticos.

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────┐
│         Frontend Web (HTML5 + Bootstrap 5)    │
│    Dashboard Admin + Chart.js Visualizations  │
└──────────────────┬───────────────────────────┘
                   │ REST APIs + JWT Auth
┌──────────────────▼───────────────────────────┐
│              Django Backend (Python 3.12)     │
├──────────────────────────────────────────────┤
│  Authentication  │  ETL Engine  │  Analytics  │
│  (JWT + Roles)   │  (Pandas)    │  (NumPy)    │
├──────────────────┼──────────────┼─────────────┤
│  ML Module       │  Dashboard   │  Reports    │
│  (Scikit-Learn)  │  (KPIs)      │  (PDF/Excel)│
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│              MySQL 8.0 Database               │
│   pacientes │ etl_history │ ml_models         │
└──────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
healthcare-etl-platform/
├── backend/
│   ├── config/
│   │   ├── settings.py       # Configuración Django
│   │   └── urls.py           # Rutas principales
│   ├── apps/
│   │   ├── authentication/   # JWT + Roles (Admin/Médico/Analista)
│   │   ├── etl/              # Motor ETL + modelos Paciente/ETLHistory
│   │   ├── analytics/        # KPIs, estadísticas, segmentación
│   │   ├── ml/               # Entrenamiento y predicción ML
│   │   ├── dashboard/        # API KPIs + vistas frontend
│   │   └── reports/          # Exportación PDF/Excel/CSV
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   └── templates/
│       ├── base.html         # Layout base con sidebar
│       ├── auth/login.html   # Página de login
│       ├── dashboard/        # Dashboard principal + Pacientes
│       ├── etl/              # Módulo ETL
│       ├── analytics/        # Analítica y gráficas
│       ├── ml/               # Machine Learning
│       └── reports/          # Exportación de reportes
├── datasets/
│   └── dataset_clinico_etl_1800_registros.xlsx
├── docs/
│   └── setup_mysql.sql       # Script SQL inicial
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile.backend
├── logs/                     # Logs ETL
├── ml_models/                # Modelos entrenados (.joblib)
├── setup.sh                  # Script instalación Linux/Mac
├── setup.ps1                 # Script instalación Windows
└── README.md
```

---

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.12+
- MySQL 8.0+
- pip / virtualenv

### Paso 1 — Configurar MySQL
```sql
-- En MySQL como root:
mysql -u root -p < docs/setup_mysql.sql
```

### Paso 2 — Variables de entorno
```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tus credenciales MySQL
```

Contenido de `.env`:
```
SECRET_KEY=tu-clave-secreta-segura
DEBUG=True
DB_NAME=healthanalytics_db
DB_USER=healthanalytics
DB_PASSWORD=HealthAnalytics2024!
DB_HOST=localhost
DB_PORT=3306
```

### Paso 3 — Instalación automática

**Linux / Mac:**
```bash
chmod +x setup.sh && ./setup.sh
```

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

### Instalación Manual
```bash
# 1. Entorno virtual
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Dependencias
pip install -r backend/requirements.txt

# 3. Migraciones
cd backend
python manage.py migrate

# 4. Usuarios iniciales
python manage.py seed_users

# 5. Servidor
python manage.py runserver
```

### Con Docker
```bash
cd docker
docker-compose up --build
```

---

## 🌐 URLs del Sistema

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/` | Dashboard principal |
| `http://localhost:8000/login/` | Inicio de sesión |
| `http://localhost:8000/pacientes/` | Lista de pacientes |
| `http://localhost:8000/etl/` | Módulo ETL |
| `http://localhost:8000/analytics/` | Analítica de datos |
| `http://localhost:8000/ml/` | Machine Learning |
| `http://localhost:8000/reportes/` | Exportar reportes |
| `http://localhost:8000/api/docs/` | Swagger OpenAPI |

---

## 🔑 Credenciales de Acceso

| Rol | Email | Contraseña |
|-----|-------|------------|
| Administrador | `admin@healthanalytics.com` | `Admin1234!` |
| Médico | `medico@healthanalytics.com` | `Medico1234!` |
| Analista | `analista@healthanalytics.com` | `Analista1234!` |

---

## 📡 APIs REST

| Endpoint | Método | Descripción | Rol |
|----------|--------|-------------|-----|
| `/api/auth/login/` | POST | Login JWT | Público |
| `/api/auth/logout/` | POST | Cerrar sesión | Autenticado |
| `/api/auth/me/` | GET | Perfil usuario | Autenticado |
| `/api/pacientes/` | GET | Lista pacientes | Autenticado |
| `/api/etl/run/` | POST | Ejecutar ETL base | Admin/Analista |
| `/api/etl/upload/` | POST | Subir CSV/Excel | Admin/Analista |
| `/api/etl/historial/` | GET | Historial ETL | Autenticado |
| `/api/analytics/kpis/` | GET | KPIs médicos | Autenticado |
| `/api/analytics/estadisticas/` | GET | Estadística descriptiva | Autenticado |
| `/api/analytics/segmentacion/riesgo/` | GET | Segmentación por riesgo | Autenticado |
| `/api/analytics/pacientes-criticos/` | GET | Pacientes críticos | Autenticado |
| `/api/ml/train/` | POST | Entrenar modelo ML | Admin/Analista |
| `/api/ml/predict/` | POST | Predicción individual | Autenticado |
| `/api/ml/info/` | GET | Info modelo activo | Autenticado |
| `/api/dashboard/kpis/` | GET | KPIs dashboard | Autenticado |
| `/api/reportes/csv/` | GET | Exportar CSV | Autenticado |
| `/api/reportes/excel/` | GET | Exportar Excel | Autenticado |
| `/api/reportes/pdf/` | GET | Exportar PDF | Autenticado |

---

## 🔄 Flujo ETL

```
Dataset Excel/CSV
       ↓
   EXTRACT
   ├── Leer archivo (Excel/CSV)
   ├── Registrar fuente y logs
   └── Contar registros
       ↓
   TRANSFORM
   ├── Eliminar duplicados (id_paciente)
   ├── Convertir tipos (edad→int, glucosa→float)
   ├── Validar rangos clínicos
   ├── Tratar valores nulos (media/mediana/moda)
   ├── Normalizar categorías (sexo, diagnóstico)
   ├── Calcular IMC (peso/altura²)
   └── Clasificar riesgo (Bajo/Medio/Alto/Crítico)
       ↓
    LOAD
   ├── Bulk insert en MySQL
   ├── Update registros existentes
   ├── Registrar log ETL
   └── Generar histórico
```

---

## 🤖 Machine Learning

### Modelos disponibles
- **Random Forest** (recomendado) — Mayor precisión
- **Regresión Logística** — Interpretable y rápido
- **Árbol de Decisión** — Visualizable

### Variables predictoras
`IMC`, `Edad`, `Glucosa`, `Colesterol`, `Presión Sistólica`, `Presión Diastólica`, `Frecuencia Cardíaca`, `Fumador`, `Antecedentes Familiares`, `Consumo Alcohol`, `Saturación O₂`, `Temperatura`

### Métricas mostradas
- Accuracy, Precision, Recall, F1-Score
- Matriz de confusión
- Importancia de características
- Reporte por clase (Bajo/Medio/Alto/Crítico)

---

## 🔒 Seguridad

- **JWT Authentication** con refresh tokens y blacklist
- **RBAC** (Role-Based Access Control): Admin / Médico / Analista
- **CSRF Protection** habilitado en Django
- **Validación de datos** en ETL y APIs
- **Sanitización** de inputs en todas las vistas
- Contraseñas hasheadas con `PBKDF2`

---

## 📊 Dataset Clínico

El archivo `datasets/dataset_clinico_etl_1800_registros.xlsx` contiene:
- **1800 registros** clínicos simulados
- Valores nulos intencionales
- Duplicados
- Tipos de datos incorrectos (`"Treinta"`, `"Alta"`)
- Valores atípicos (`peso=420kg`)
- Errores ortográficos (`"hipertencion"`, `"hipertensíon"`)

### Variables incluidas
`id_paciente`, `nombres`, `apellidos`, `edad`, `sexo`, `peso`, `altura`, `IMC`, `presión_sistólica`, `presión_diastólica`, `frecuencia_cardiaca`, `glucosa`, `colesterol`, `saturación_oxígeno`, `temperatura`, `antecedentes_familiares`, `fumador`, `consumo_alcohol`, `actividad_física`, `diagnóstico_preliminar`, `riesgo_enfermedad`, `fecha_consulta`

---

## 🏥 Detección de Pacientes Críticos

Un paciente es marcado como **Crítico** si cumple cualquier condición:
- Presión sistólica **> 180 mmHg**
- Glucosa **> 300 mg/dL**
- Saturación de O₂ **< 85%**

---

## 📐 Clasificación IMC

| IMC | Clasificación |
|-----|--------------|
| < 18.5 | Bajo peso |
| 18.5 – 24.9 | Normal |
| 25 – 29.9 | Sobrepeso |
| ≥ 30 | Obesidad |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12, Django 4.2, DRF 3.15 |
| Auth | JWT (SimpleJWT) + Roles personalizados |
| ETL | Pandas 2.2, NumPy 1.26 |
| ML | Scikit-Learn 1.5, Joblib |
| Base de datos | MySQL 8.0 |
| Frontend | HTML5, Bootstrap 5.3, Chart.js 4.4 |
| Exportación | ReportLab (PDF), XlsxWriter (Excel) |
| API Docs | drf-yasg (Swagger/OpenAPI) |
| Estadísticas | SciPy 1.13 |

---

## 📜 Licencia

MIT — Proyecto académico para Reto Técnico SENA FullStack + Data Analytics.

**Fecha de entrega:** 15 de junio de 2026
