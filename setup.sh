#!/bin/bash
# =============================================================
# HealthAnalytics IPS — Script de Instalación y Configuración
# =============================================================
set -e

echo "=================================================="
echo "  HealthAnalytics IPS — Setup Script"
echo "=================================================="

# Verificar Python 3.12+
python3 --version || { echo "ERROR: Python 3.12+ es requerido"; exit 1; }

# Crear entorno virtual
echo ""
echo "[1/6] Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "[2/6] Instalando dependencias Python..."
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
echo "✓ Dependencias instaladas"

# Configurar variables de entorno
echo "[3/6] Configurando variables de entorno..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✓ Archivo .env creado desde .env.example"
    echo "  → EDITA backend/.env con tus credenciales de MySQL antes de continuar"
    echo "  → Luego vuelve a ejecutar este script o continúa manualmente"
fi

# Crear directorios necesarios
echo "[4/6] Creando directorios..."
mkdir -p logs ml_models
touch logs/.gitkeep ml_models/.gitkeep
echo "✓ Directorios creados"

# Migraciones Django
echo "[5/6] Ejecutando migraciones..."
cd backend
python manage.py migrate
echo "✓ Migraciones aplicadas"

# Crear usuarios iniciales
echo "[6/6] Creando usuarios de prueba..."
python manage.py seed_users
echo "✓ Usuarios creados"

echo ""
echo "=================================================="
echo "  ✅ Instalación completada"
echo "=================================================="
echo ""
echo "  Credenciales de acceso:"
echo "  ┌─────────────────────────────────────────────┐"
echo "  │ admin@healthanalytics.com   / Admin1234!    │"
echo "  │ medico@healthanalytics.com  / Medico1234!   │"
echo "  │ analista@healthanalytics.com / Analista1234!│"
echo "  └─────────────────────────────────────────────┘"
echo ""
echo "  Para iniciar el servidor:"
echo "  cd backend && python manage.py runserver"
echo ""
echo "  URL: http://localhost:8000"
echo "  API Docs: http://localhost:8000/api/docs/"
echo "=================================================="
