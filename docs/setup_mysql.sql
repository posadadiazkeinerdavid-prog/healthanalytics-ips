-- ============================================================
-- HealthAnalytics IPS — Script de Configuración MySQL
-- Ejecutar como root: mysql -u root -p < setup_mysql.sql
-- ============================================================

-- 1. Crear base de datos
CREATE DATABASE IF NOT EXISTS healthanalytics_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE healthanalytics_db;

-- 2. Crear usuario de aplicación
CREATE USER IF NOT EXISTS 'healthanalytics'@'localhost'
    IDENTIFIED BY 'HealthAnalytics2024!';

GRANT ALL PRIVILEGES ON healthanalytics_db.* TO 'healthanalytics'@'localhost';
FLUSH PRIVILEGES;

-- ============================================================
-- NOTA: Las tablas son creadas automáticamente por Django.
-- Después de ejecutar este script, corre:
--   cd backend
--   python manage.py migrate
--   python manage.py seed_users
-- ============================================================

SELECT 'Base de datos healthanalytics_db creada exitosamente' AS mensaje;
SHOW DATABASES LIKE 'healthanalytics_db';
