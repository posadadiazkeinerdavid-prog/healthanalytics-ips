# =============================================================
# HealthAnalytics IPS — Script de Instalación Windows (PowerShell)
# Ejecutar: .\setup.ps1
# =============================================================

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  HealthAnalytics IPS — Setup Script (Windows)"   -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Crear entorno virtual
Write-Host "`n[1/6] Creando entorno virtual..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
Write-Host "[2/6] Instalando dependencias Python..." -ForegroundColor Yellow
pip install --upgrade pip -q
pip install -r backend\requirements.txt -q
Write-Host "✓ Dependencias instaladas" -ForegroundColor Green

# Variables de entorno
Write-Host "[3/6] Configurando variables de entorno..." -ForegroundColor Yellow
if (-Not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✓ Archivo .env creado — EDITA las credenciales MySQL" -ForegroundColor Green
}

# Directorios
Write-Host "[4/6] Creando directorios..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs", "ml_models" | Out-Null
Write-Host "✓ Directorios creados" -ForegroundColor Green

# Migraciones
Write-Host "[5/6] Ejecutando migraciones..." -ForegroundColor Yellow
Set-Location backend
python manage.py migrate
Write-Host "✓ Migraciones aplicadas" -ForegroundColor Green

# Usuarios iniciales
Write-Host "[6/6] Creando usuarios de prueba..." -ForegroundColor Yellow
python manage.py seed_users
Write-Host "✓ Usuarios creados" -ForegroundColor Green

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "  ✅ Instalación completada"                        -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "`n  Credenciales:"
Write-Host "  admin@healthanalytics.com    / Admin1234!"
Write-Host "  medico@healthanalytics.com   / Medico1234!"
Write-Host "  analista@healthanalytics.com / Analista1234!"
Write-Host "`n  Iniciar servidor:"
Write-Host "  python manage.py runserver"
Write-Host "`n  URL: http://localhost:8000"
Write-Host "  API: http://localhost:8000/api/docs/"
Write-Host "==================================================" -ForegroundColor Cyan
