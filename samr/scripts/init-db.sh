#!/bin/bash
set -e

echo "Inicializando bases de datos (PostgreSQL)..."

export PGPASSWORD=${DB_PASSWORD}
PSQL="psql -h postgres -U samr"

# Crear rol de manera idempotente
$PSQL -tc "SELECT 1 FROM pg_roles WHERE rolname = 'samr'" | grep -q 1 || $PSQL -c "CREATE ROLE samr WITH LOGIN PASSWORD '${DB_PASSWORD}';"

# Crear bases de datos
DATABASES=(
    "auth_db"
    "patient_db"
    "solicitud_db"
    "monitoring_db"
    "evaluacion_db"
    "teleconsult_db"
    "emergency_db"
    "cierre_db"
    "historial_db"
    "audit_db"
    "admin_db"
)

for db in "${DATABASES[@]}"; do
    $PSQL -tc "SELECT 1 FROM pg_database WHERE datname = '$db'" | grep -q 1 || $PSQL -c "CREATE DATABASE $db OWNER samr ENCODING 'UTF8';"
done

# Revoke en audit_db para inmutabilidad (condicionado a si la tabla ya existe)
psql -h postgres -U samr -d audit_db -c "
DO \$\$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'audit_log') THEN
        EXECUTE 'REVOKE UPDATE, DELETE ON audit_log FROM samr;';
    END IF;
END
\$\$;
"

# Ejecutar migraciones si existen
echo "Ejecutando migraciones..."
for d in ../services/*/; do
    if [ -f "$d/manage.py" ]; then
        echo "Migrando $d..."
        (cd "$d" && python manage.py migrate || true)
    fi
done

echo "Base de datos inicializada."
