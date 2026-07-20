#!/bin/bash
set -euo pipefail

echo "Inicializando las 11 bases PostgreSQL aisladas de SAMR..."

DATABASES=(
  auth_db patient_db solicitud_db monitoring_db evaluacion_db teleconsult_db
  emergency_db cierre_db historial_db audit_db admin_db
)

for db in "${DATABASES[@]}"; do
  if ! psql --username "${POSTGRES_USER}" --dbname postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='${db}'" | grep -q 1; then
    createdb --username "${POSTGRES_USER}" --owner "${POSTGRES_USER}" \
      --encoding UTF8 "${db}"
  fi
done

echo "Bases PostgreSQL de SAMR listas."
