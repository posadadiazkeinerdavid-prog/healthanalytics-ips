# 🏥 HealthAnalytics IPS — Plataforma Inteligente de Analítica Clínica

> **Reto Técnico FullStack + Data Analytics + ETL + Machine Learning**  
> Plataforma web inteligente para detección de riesgo médico mediante procesamiento de datos clínicos.

---

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Variables de Entorno](#variables-de-entorno)
- [Base de Datos](#base-de-datos)
- [Ejecución del Proyecto](#ejecución-del-proyecto)
- [APIs REST](#apis-rest)
- [Módulos del Sistema](#módulos-del-sistema)
- [Machine Learning](#machine-learning)
- [Roles y Permisos](#roles-y-permisos)
- [Credenciales de Prueba](#credenciales-de-prueba)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Dependencias](#dependencias)

---

## Descripción General

HealthAnalytics IPS es una aplicación web FullStack desarrollada con **Python/Django** que permite:

- ✅ Ejecutar un proceso ETL completo (Extract, Transform, Load) sobre datos clínicos
- ✅ Limpiar, validar y transformar datos médicos con inconsistencias reales
- ✅ Detectar automáticamente pacientes críticos por umbrales clínicos
- ✅ Clasificar pacientes por nivel de riesgo (Bajo / Medio / Alto / Crítico)
- ✅ Entrenar y ejecutar modelos de Machine Learning predictivos
- ✅ Visualizar métricas e indicadores clínicos mediante dashboards interactivos
- ✅ Exportar reportes en PDF, Excel y CSV
- ✅ Administrar usuarios con control de acceso basado en roles (RBAC)

---

## Tecnologías Utilizadas

### Backend
| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12+ | Lenguaje principal |
| Django | 5.2.2 | Framework web |
| Django REST Framework | 3.17.1 | APIs REST |
| SimpleJWT | 5.5.1 | Autenticación JWT |
| Pandas | 3.0.3 | Procesamiento ETL |
| NumPy | 2.4.6 | Cálculos numéricos |
| Scikit-Learn | 1.8.0 | Machine Learning |
| SciPy | 1.17.1 | Estadística descriptiva |
| drf-yasg | 1.21.15 | Documentación Swagger |
| ReportLab | 4.5.1 | Generación de PDFs |
| XlsxWriter | 3.2.9 | Generación de Excel |
| PyMySQL | 1.2.0 | Conector MySQL |
| Joblib | 1.5.3 | Persistencia de modelos ML |
| Gunicorn | 26.0.0 | Servidor WSGI |
| Whitenoise | 6.12.0 | Archivos estáticos |

### Frontend
| Tecnología | Versión | Uso |
|---|---|---|
| Bootstrap | 5.3.0 | UI / Diseño responsivo |
| Chart.js | 4.4.0 | Gráficas interactivas |
| Bootstrap Icons | 1.11.0 | Iconografía |
| JavaScript (vanilla) | ES6+ | Lógica de interfaz |

### Base de Datos
- **MySQL** (principal) — compatible con PostgreSQL cambiando el driver

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────┐
│           Frontend Web (Django Templates)│
│   Dashboard  │  ETL  │  ML  │  Reportes │
└──────────────────┬──────────────────────┘
                   │ REST APIs (JWT)
┌──────────────────▼──────────────────────┐
│              Django Backend             │
├─────────────────────────────────────────┤
│  Authentication & Roles (JWT + RBAC)    │
│  ETL Engine (Extract/Transform/Load)    │
│  Analytics Module (KPIs + Estadísticas) │
│  ML Prediction Module (3 modelos)       │
│  Reporting Module (PDF/Excel/CSV)       │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│           MySQL / PostgreSQL            │
│          Base de Datos Clínica          │
└─────────────────────────────────────────┘
```

---

## Requisitos Previos

Antes de instalar el proyecto, asegúrese de tener:

- **Python 3.12 o superior** — [Descargar](https://www.python.org/downloads/)
- **MySQL 8.0+** — [Descargar](https://dev.mysql.com/downloads/)
- **Git** — [Descargar](https://git-scm.com/)
- **pip** (incluido con Python)

Verificar versiones:
```bash
python --version    # Python 3.12+
mysql --version     # MySQL 8.0+
git --version
```

---

## Instalación y Configuración

### Opción 1: Script automático (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/healthanalytics-ips.git
cd healthanalytics-ips

# 2. Crear la base de datos en MySQL
mysql -u root -p -e "CREATE DATABASE healthanalytics_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus credenciales de MySQL

# 4. Ejecutar el script de instalación
chmod +x setup.sh
./setup.sh
```

### Opción 2: Instalación manual paso a paso

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/healthanalytics-ips.git
cd healthanalytics-ips

# 2. Crear entorno virtual
python -m venv venv

# Activar en Linux/Mac:
source venv/bin/activate
# Activar en Windows:
venv\Scripts\activate

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Crear base de datos en MySQL
mysql -u root -p
CREATE DATABASE healthanalytics_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 5. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env (ver sección Variables de Entorno)

# 6. Crear directorios necesarios
mkdir -p logs ml_models

# 7. Ejecutar migraciones
cd backend
python manage.py migrate

# 8. Crear usuarios de prueba
python manage.py seed_users

# 9. Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

---

## Variables de Entorno

Crear el archivo `backend/.env` con el siguiente contenido:

```env
# Django
SECRET_KEY=tu-clave-secreta-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos MySQL
DB_NAME=healthanalytics_db
DB_USER=root
DB_PASSWORD=tu_password_mysql
DB_HOST=localhost
DB_PORT=3306

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

> ⚠️ **Importante:** Nunca subas el archivo `.env` a un repositorio público. Está incluido en `.gitignore`.

---

## Base de Datos

### Crear la base de datos

```sql
CREATE DATABASE healthanalytics_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### Tablas principales

| Tabla | Descripción |
|---|---|
| `auth_users` | Usuarios del sistema con roles |
| `etl_pacientes` | Datos clínicos de pacientes (post-ETL) |
| `etl_historial` | Registro de ejecuciones ETL |
| `ml_models` | Modelos ML entrenados y sus métricas |
| `ml_predicciones` | Historial de predicciones individuales |

### Diagrama de relaciones (ERD simplificado)

```
auth_users ─────┬──── etl_historial (usuario_id)
                └──── ml_models (usuario_id)
                └──── ml_predicciones (usuario_id)

etl_pacientes (tabla independiente, cargada por ETL)
```

---

## Ejecución del Proyecto

```bash
# Activar entorno virtual
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Ir al directorio backend
cd backend

# Iniciar servidor de desarrollo
python manage.py runserver

# El sistema estará disponible en:
# http://localhost:8000
```

---

## APIs REST

La documentación interactiva de la API está disponible en:
- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`

### Endpoints principales

#### Autenticación
| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/auth/login/` | Iniciar sesión (retorna JWT) |
| POST | `/api/auth/logout/` | Cerrar sesión (invalida token) |
| POST | `/api/auth/token/refresh/` | Renovar access token |
| GET | `/api/auth/me/` | Datos del usuario autenticado |
| GET/POST | `/api/auth/usuarios/` | Listar / crear usuarios (solo Admin) |

#### Pacientes
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/pacientes/` | Listar pacientes con filtros |
| GET | `/api/pacientes/{id}/` | Detalle de un paciente |

#### ETL
| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/etl/run/` | Ejecutar ETL con dataset base |
| POST | `/api/etl/upload/` | Cargar CSV/Excel y ejecutar ETL |
| GET | `/api/etl/historial/` | Historial de ejecuciones ETL |
| GET | `/api/etl/historial/{id}/` | Detalle de una ejecución ETL |

#### Analítica
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/analytics/kpis/` | KPIs médicos principales |
| GET | `/api/analytics/estadisticas/` | Estadística descriptiva completa |
| GET | `/api/analytics/segmentacion/riesgo/` | Segmentación por riesgo |
| GET | `/api/analytics/segmentacion/sexo/` | Segmentación por sexo |
| GET | `/api/analytics/segmentacion/diagnostico/` | Segmentación por diagnóstico |
| GET | `/api/analytics/segmentacion/imc/` | Segmentación por IMC |
| GET | `/api/analytics/pacientes-criticos/` | Lista de pacientes críticos |
| GET | `/api/analytics/tendencia-edad/` | Riesgo por grupo de edad |

#### Dashboard
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/dashboard/kpis/` | KPIs completos para el panel |

#### Machine Learning
| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/ml/train/` | Entrenar modelo ML |
| POST | `/api/ml/predict/` | Predicción individual |
| POST | `/api/ml/predict/batch/` | Predicción masiva |
| GET | `/api/ml/info/` | Info del modelo activo |
| GET | `/api/ml/historial/` | Modelos entrenados |
| GET | `/api/ml/predicciones/` | Historial de predicciones |

#### Reportes
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/reportes/` | Resumen de reportes |
| GET | `/api/reportes/csv/` | Exportar pacientes a CSV |
| GET | `/api/reportes/excel/` | Exportar reporte a Excel |
| GET | `/api/reportes/pdf/` | Exportar reporte ejecutivo a PDF |

### Autenticación en las APIs

Todas las APIs (excepto login) requieren el header:

```
Authorization: Bearer <access_token>
```

---

## Módulos del Sistema

### 1. Proceso ETL

El motor ETL ejecuta tres fases:

**EXTRACT:** Lee archivos Excel (.xlsx) o CSV externos, registra la fuente y el tiempo de lectura.

**TRANSFORM** — Reglas aplicadas:
- Eliminación de duplicados por `id_paciente`
- Conversión de tipos: `edad = "Treinta"` → `NaN`, `presión_sistólica = "Alta"` → `NaN`
- Validación de rangos clínicos: `peso = 420 kg` → `NaN`, `temperatura = 28°C` → `NaN`
- Tratamiento de nulos: media (peso, glucosa), mediana (edad, presión), moda (sexo, diagnóstico)
- Normalización: errores ortográficos como `"hipertencion"` → `"Hipertensión"`
- Cálculo de IMC: `peso / altura²`
- Clasificación de riesgo automática por reglas clínicas

**Clasificación de Riesgo:**
| Riesgo | Criterios |
|---|---|
| Crítico | Presión sistólica > 180 O glucosa > 300 O saturación O₂ < 85% |
| Alto | Presión ≥ 160 O glucosa ≥ 200 O IMC ≥ 35 |
| Medio | Presión ≥ 140 O glucosa ≥ 126 O IMC ≥ 30 O colesterol ≥ 240 |
| Bajo | Ninguna condición anterior |

**LOAD:** Inserta o actualiza registros en la base de datos, guarda logs detallados y registra el historial ETL.

**Clasificación IMC:**
| IMC | Clasificación |
|---|---|
| < 18.5 | Bajo peso |
| 18.5 – 24.9 | Normal |
| 25 – 29.9 | Sobrepeso |
| > 30 | Obesidad |

---

### 2. Analítica de Datos

**Estadística descriptiva** para: edad, peso, altura, IMC, presión sistólica, presión diastólica, frecuencia cardíaca, glucosa, colesterol, saturación O₂, temperatura.

Cada variable retorna: media, mediana, moda, desviación estándar, mínimo, máximo, n.

**KPIs Médicos:**
- Total de pacientes
- Pacientes críticos / hipertensos / diabéticos / fumadores
- Distribución por nivel de riesgo
- Promedios de edad, IMC, glucosa, presión sistólica

**Detección de pacientes críticos:**
- Presión sistólica > 180 mmHg
- Glucosa > 300 mg/dL
- Saturación de oxígeno < 85%

---

## Machine Learning

### Modelos disponibles

| Modelo | Parámetros | Descripción |
|---|---|---|
| Random Forest | 100 estimadores, random_state=42 | Mejor rendimiento general |
| Regresión Logística | max_iter=500, StandardScaler | Interpretable, rápido |
| Árbol de Decisión | max_depth=8 | Visualizable |

### Variables predictoras

`IMC`, `edad`, `glucosa`, `colesterol`, `presión sistólica`, `presión diastólica`, `frecuencia cardíaca`, `fumador`, `antecedentes familiares`, `consumo alcohol`, `saturación O₂`, `temperatura`

### Variable objetivo

`riesgo_enfermedad` → clases: Bajo / Medio / Alto / Crítico

### Métricas reportadas

- **Accuracy** — proporción de predicciones correctas
- **Precision** — exactitud de las predicciones positivas
- **Recall** — cobertura de casos positivos reales
- **F1-Score** — media armónica entre precision y recall
- **Matriz de confusión** — desglose por clase
- **Feature importance** (Random Forest y Árbol de Decisión)

### Flujo ML

```
Dataset limpio (post-ETL)
        ↓
Preprocesamiento (encoding, fillna, scaling)
        ↓
Entrenamiento (80% train / 20% test)
        ↓
Evaluación (accuracy, F1, matriz de confusión)
        ↓
Persistencia del modelo (joblib)
        ↓
Predicción individual o masiva
        ↓
Visualización en Dashboard
```

---

## Roles y Permisos

| Rol | Dashboard | Pacientes | ETL | Analítica | ML | Reportes | Usuarios |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Administrador | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Médico | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| Analista | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

---

## Credenciales de Prueba

Generadas automáticamente por `python manage.py seed_users`:

| Rol | Email | Contraseña |
|---|---|---|
| Administrador | `admin@healthanalytics.com` | `Admin1234!` |
| Médico | `medico@healthanalytics.com` | `Medico1234!` |
| Analista | `analista@healthanalytics.com` | `Analista1234!` |

> ⚠️ Cambiar estas credenciales antes de desplegar en producción.

---

## Estructura del Proyecto

```
healthanalytics-ips/
│
├── backend/
│   ├── config/
│   │   ├── settings.py          # Configuración Django
│   │   ├── urls.py              # URLs raíz
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── authentication/      # Login, JWT, roles, usuarios
│   │   ├── etl/                 # Motor ETL, modelo Paciente, historial
│   │   ├── analytics/           # KPIs, estadísticas, segmentación
│   │   ├── ml/                  # Entrenamiento, predicción, métricas
│   │   ├── dashboard/           # Vistas del panel principal
│   │   └── reports/             # Exportación PDF/Excel/CSV
│   │
│   ├── .env                     # Variables de entorno (no subir a Git)
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── templates/
│   │   ├── base.html            # Template base con sidebar y topbar
│   │   ├── auth/login.html
│   │   ├── dashboard/index.html
│   │   ├── dashboard/pacientes.html
│   │   ├── etl/index.html
│   │   ├── analytics/index.html
│   │   ├── ml/index.html
│   │   └── reports/index.html
│   └── static/
│       ├── css/healthanalytics.css
│       └── js/charts.js
│
├── datasets/                    # Dataset clínico simulado (1800 registros)
├── docs/                        # Diagramas y documentación técnica
├── ml_models/                   # Modelos ML entrenados (generados en runtime)
├── logs/                        # Logs del sistema (generados en runtime)
├── setup.sh                     # Script de instalación automática
└── README.md
```

---

## Dependencias

Instalar todas las dependencias con:

```bash
pip install -r backend/requirements.txt
```

Lista completa de dependencias (`requirements.txt`):

```
Django==5.2.2
djangorestframework==3.17.1
djangorestframework-simplejwt==5.5.1
django-cors-headers==4.9.0
drf-yasg==1.21.15
pandas==3.0.3
numpy==2.4.6
scikit-learn==1.8.0
scipy==1.17.1
joblib==1.5.3
PyMySQL==1.2.0
psycopg2-binary==2.9.12
python-dotenv==1.2.2
reportlab==4.5.1
xlsxwriter==3.2.9
openpyxl==3.1.5
Pillow==12.2.0
gunicorn==26.0.0
whitenoise==6.12.0
dj-database-url==3.1.2
PyJWT==2.13.0
```

---

## Solución de Problemas Frecuentes

**Error de conexión a MySQL:**
```bash
# Verificar que MySQL esté corriendo
sudo systemctl status mysql   # Linux
# Verificar credenciales en backend/.env
```

**Error de migraciones:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Error "No hay suficientes datos para ML":**
> Primero ejecute el proceso ETL desde el módulo correspondiente para cargar pacientes en la BD.

**Puerto 8000 ocupado:**
```bash
python manage.py runserver 8080
```

---

## Fecha de Entrega

**15 de junio de 2026** — Modalidad: Individual

---

*Desarrollado como Reto Técnico FullStack + Data Analytics + ETL + Machine Learning para HealthAnalytics IPS.*
