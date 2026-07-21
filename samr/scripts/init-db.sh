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

echo "Aplicando DDL y reglas de negocio por Schema..."

# auth_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "auth_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS auth_user (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email           VARCHAR(255) UNIQUE NOT NULL,
        password_hash   VARCHAR(255) NOT NULL,
        role            VARCHAR(50) NOT NULL,
        failed_attempts SMALLINT DEFAULT 0,
        locked_until    TIMESTAMPTZ NULL,
        created_at      TIMESTAMPTZ DEFAULT now()
    );
EOSQL

# patient_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "patient_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS patients (
        id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id             UUID NOT NULL,
        cedula_encrypted    BYTEA NOT NULL,
        blood_type          VARCHAR(5),
        allergies           JSONB,
        chronic_conditions  JSONB,
        latitude            DECIMAL(9,6),
        longitude           DECIMAL(9,6),
        consent_data        BOOLEAN DEFAULT FALSE,
        consent_ai          BOOLEAN DEFAULT FALSE,
        consent_sharing     BOOLEAN DEFAULT FALSE
    );
EOSQL

# solicitud_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "solicitud_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS solicitudes (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        patient_id      UUID NOT NULL,
        sintomas        JSONB,
        datos_biomedicos JSONB,
        fuente          VARCHAR(20) DEFAULT 'chatbot',
        estado          VARCHAR(20) DEFAULT 'pendiente',
        created_at      TIMESTAMPTZ DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS vity_conversations (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        patient_id      UUID NOT NULL,
        messages        JSONB NOT NULL DEFAULT '[]',
        created_at      TIMESTAMPTZ DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS idx_vity_messages_gin ON vity_conversations USING GIN (messages);

    CREATE TABLE IF NOT EXISTS faq_entries (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        question    TEXT NOT NULL,
        answer      TEXT NOT NULL,
        updated_at  TIMESTAMPTZ DEFAULT now()
    );
EOSQL

# monitoring_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "monitoring_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS vital_signs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        device_id UUID NOT NULL,
        patient_id UUID NOT NULL,
        value JSONB, 
        recorded_at TIMESTAMPTZ DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS monitoring_alerts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        patient_id UUID NOT NULL, 
        severity VARCHAR(20), 
        created_at TIMESTAMPTZ DEFAULT now()
    );
EOSQL

# evaluacion_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "evaluacion_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS evaluaciones_riesgo (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        solicitud_id    UUID NOT NULL,
        nivel_riesgo    VARCHAR(20) NOT NULL,
        fuentes_rag     JSONB,
        created_at      TIMESTAMPTZ DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS matchings (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        evaluacion_id   UUID REFERENCES evaluaciones_riesgo(id),
        professional_id UUID NOT NULL,
        center_id       UUID NOT NULL,
        score           DECIMAL(5,2)
    );

    CREATE TABLE IF NOT EXISTS centros_disponibles_cache (
        center_id   UUID PRIMARY KEY,
        nombre      VARCHAR(255),
        disponible  BOOLEAN DEFAULT TRUE
    );
EOSQL

# teleconsult_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "teleconsult_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS teleconsults (
        id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        patient_id     UUID NOT NULL, 
        professional_id UUID NOT NULL,
        emergency_id   UUID NULL, 
        room_token VARCHAR(64) UNIQUE NOT NULL,
        diagnosis      TEXT, 
        ai_recommendation JSONB,
        status         VARCHAR(20) DEFAULT 'active', 
        closed_at TIMESTAMPTZ NULL
    );
EOSQL

# emergency_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "emergency_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS emergency_cases (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        patient_id    UUID NOT NULL,
        triage_level  VARCHAR(20) NOT NULL,
        status        VARCHAR(30) DEFAULT 'pending',
        created_at    TIMESTAMPTZ DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS guias_primeros_auxilios (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        emergency_id    UUID REFERENCES emergency_cases(id),
        contenido       TEXT NOT NULL,
        fecha_generacion TIMESTAMPTZ DEFAULT now()
    );
EOSQL

# cierre_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "cierre_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS clinical_cases (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        patient_id    UUID NOT NULL, 
        teleconsult_id UUID NULL, 
        emergency_id UUID NULL,
        clinical_notes TEXT, 
        integrity_hash VARCHAR(64),
        status        VARCHAR(20) DEFAULT 'open', 
        closed_at TIMESTAMPTZ NULL
    );
EOSQL

# historial_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "historial_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS expedientes_consolidados (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        patient_id      UUID NOT NULL,
        eventos         JSONB NOT NULL DEFAULT '[]',
        updated_at      TIMESTAMPTZ DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS idx_expediente_gin ON expedientes_consolidados USING GIN (eventos);
EOSQL

# audit_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "audit_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS audit_log (
        id            BIGSERIAL PRIMARY KEY,
        event_type    VARCHAR(100) NOT NULL,
        actor_id      UUID, 
        payload JSONB NOT NULL,
        ai_confidence DECIMAL(4,3) NULL, 
        ai_explainability JSONB NULL,
        created_at    TIMESTAMPTZ DEFAULT now()
    );
    
    -- Inmutabilidad a nivel de motor (regla de negocio principal)
    REVOKE UPDATE, DELETE ON audit_log FROM "${POSTGRES_USER}";

    CREATE TABLE IF NOT EXISTS audit_reviews (
        id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        audit_log_id        BIGINT NOT NULL,
        estado_revision     VARCHAR(20) DEFAULT 'pendiente',
        revisado_por        UUID NULL,
        comentario          TEXT NULL,
        fecha_revision      TIMESTAMPTZ NULL,
        created_at          TIMESTAMPTZ DEFAULT now()
    );
EOSQL

# admin_db
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "admin_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS centers (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name        VARCHAR(255) NOT NULL,
        type        VARCHAR(50),
        latitude    DECIMAL(9,6), 
        longitude DECIMAL(9,6),
        status      VARCHAR(20) DEFAULT 'pending_validation'
    );

    CREATE TABLE IF NOT EXISTS professionals (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        center_id   UUID REFERENCES centers(id),
        specialty   VARCHAR(100),
        available   BOOLEAN DEFAULT TRUE,
        current_load SMALLINT DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS devices (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        patient_id    UUID NOT NULL,
        device_type   VARCHAR(50),
        registered_by UUID NOT NULL,
        active        BOOLEAN DEFAULT TRUE
    );
EOSQL

echo "Bases PostgreSQL de SAMR listas y schemas inicializados con DDL seguro."
