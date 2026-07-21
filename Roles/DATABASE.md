# SAMR — Base de Datos y Persistencia
## Rama `data/persistence-db`

> Los 11 schemas PostgreSQL (Supabase), uno por servicio con base de datos propia, más las convenciones de modelado. Para responsabilidades de negocio ver `arch/system-design`; para el flujo de eventos que dispara cada escritura ver `logic/core-services`.

---

# 1. Convenciones Generales

- **UUID como clave primaria** en todas las tablas de negocio (`gen_random_uuid()`), excepto `audit_log` que usa `BIGSERIAL` (el orden de inserción es parte de la evidencia de auditoría).
- **Convención de nombres de schema:** `{dominio}_db` en minúsculas — `auth_db`, `patient_db`, `solicitud_db`, `monitoring_db`, `evaluacion_db`, `teleconsult_db`, `emergency_db`, `cierre_db`, `historial_db`, `audit_db`, `admin_db` (**11 schemas** en total).
- **JSONB para esquema dinámico** (conversaciones del bot, expediente consolidado, payload de eventos en `audit_log`) — nunca una tabla EAV ni columnas nullable especulativas.
- **Inmutabilidad declarativa:** cualquier tabla de auditoría/trazabilidad debe tener su `REVOKE UPDATE, DELETE` documentado en `scripts/init-db.sh`, no solo confiado al código de la aplicación.
- **Índices obligatorios:** `patient_id` en toda tabla que lo contenga (consulta más frecuente del sistema); `GIN` sobre columnas `JSONB` consultadas por contenido.
- **Sin Foreign Keys entre schemas** — las referencias a `patient_id`/`user_id`/`device_id`/`center_id` de otro servicio son *lógicas* (UUID), nunca `REFERENCES` cruzado. La consistencia se garantiza por evento (ver `logic/core-services`), no por constraint de base de datos.
- **Script de inicialización (`scripts/init-db.sh`):** crea los 11 schemas de negocio, ejecuta `python manage.py migrate` de cada servicio, y aplica los `REVOKE` de la tabla `audit_log`.
- Motor: **PostgreSQL 16** (Supabase) para todo dato persistente. Redis solo para cache de lecturas y Channel Layer de WebSocket — nunca como almacén de negocio.

---

# 2. Schema por Servicio

## 2.1 `auth_db` — `auth-service` (transversal)
```sql
CREATE TABLE auth_user (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(50) NOT NULL,  -- patient|professional|nurse|center_admin|system_admin|dpd_delegate
    failed_attempts SMALLINT DEFAULT 0,
    locked_until    TIMESTAMPTZ NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

## 2.2 `patient_db` — `patient-service` (M1)
```sql
CREATE TABLE patients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,           -- referencia lógica a auth_user.id
    cedula_encrypted    BYTEA NOT NULL,           -- Fernet AES-128 (ver sec/security-hardening)
    blood_type          VARCHAR(5),
    allergies           TEXT[],
    chronic_conditions  TEXT[],
    latitude            DECIMAL(9,6),
    longitude           DECIMAL(9,6),
    consent_data        BOOLEAN DEFAULT FALSE,
    consent_ai          BOOLEAN DEFAULT FALSE,
    consent_sharing     BOOLEAN DEFAULT FALSE
);
```

## 2.3 `solicitud_db` — `solicitud-service` (M1)
```sql
CREATE TABLE solicitudes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL,
    sintomas        TEXT[],
    datos_biomedicos JSONB,
    fuente          VARCHAR(20) DEFAULT 'chatbot',  -- chatbot|iot_anomalia|manual
    estado          VARCHAR(20) DEFAULT 'pendiente', -- pendiente|validada|rechazada
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE vity_conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL,
    messages        JSONB NOT NULL DEFAULT '[]',  -- esquema dinámico
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_vity_messages_gin ON vity_conversations USING GIN (messages);

CREATE TABLE faq_entries (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question    TEXT NOT NULL,
    answer      TEXT NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT now()
);
```
Redis (no negocio): `vity_cache:{hash_del_mensaje}` (TTL 60s) — cache de respuestas de FAQ.

## 2.4 `monitoring_db` — `monitoring-service` (M1)
```sql
CREATE TABLE vital_signs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL,   -- referencia lógica a devices.id en admin_db
    patient_id UUID NOT NULL,
    value JSONB, recorded_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE monitoring_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL, severity VARCHAR(20), created_at TIMESTAMPTZ DEFAULT now()
);
```
Redis (no negocio): `vitals:{patient_id}` (TTL 120s, últimas 50 lecturas).

## 2.5 `evaluacion_db` — `evaluacion-service` (M2)
```sql
CREATE TABLE evaluaciones_riesgo (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id    UUID NOT NULL,
    nivel_riesgo    VARCHAR(20) NOT NULL,  -- critico|alto|medio|bajo
    fuentes_rag     JSONB,                 -- trazabilidad RNF-15
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE matchings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluacion_id   UUID REFERENCES evaluaciones_riesgo(id),
    professional_id UUID NOT NULL,
    center_id       UUID NOT NULL,
    score           DECIMAL(5,2)
);

-- Espejo de solo lectura de admin_db.centers, actualizado por evento
-- (center.validated / center.rejected — ver logic/core-services)
CREATE TABLE centros_disponibles_cache (
    center_id   UUID PRIMARY KEY,
    nombre      VARCHAR(255),
    disponible  BOOLEAN DEFAULT TRUE
);
```

## 2.6 `teleconsult_db` — `teleconsult-service` (M3)
```sql
CREATE TABLE teleconsults (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id     UUID NOT NULL, professional_id UUID NOT NULL,
    emergency_id   UUID NULL, room_token VARCHAR(64) UNIQUE NOT NULL,
    diagnosis      TEXT, ai_recommendation JSONB,
    status         VARCHAR(20) DEFAULT 'active', closed_at TIMESTAMPTZ NULL
);
```
Redis (no negocio): `room:{room_token}` (TTL 3600s: estado de sala).

## 2.7 `emergency_db` — `emergency-service` (M3)
```sql
CREATE TABLE emergency_cases (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id    UUID NOT NULL,
    triage_level  VARCHAR(20) NOT NULL,
    status        VARCHAR(30) DEFAULT 'pending', -- pending|dispatched|closed
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE guias_primeros_auxilios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emergency_id    UUID REFERENCES emergency_cases(id),
    contenido       TEXT NOT NULL,
    fecha_generacion TIMESTAMPTZ DEFAULT now()
);
```

## 2.8 `cierre_db` — `cierre-caso-service` (M3)
```sql
CREATE TABLE clinical_cases (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id    UUID NOT NULL, teleconsult_id UUID NULL, emergency_id UUID NULL,
    clinical_notes TEXT, integrity_hash VARCHAR(64),  -- SHA-256
    status        VARCHAR(20) DEFAULT 'open', closed_at TIMESTAMPTZ NULL
);
```

## 2.9 `historial_db` — `historial-interop-service` (M4)
```sql
CREATE TABLE expedientes_consolidados (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL,
    eventos         JSONB NOT NULL DEFAULT '[]',  -- solicitudes, teleconsultas, emergencias, decisiones IA
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_expediente_gin ON expedientes_consolidados USING GIN (eventos);
```
Redis (no negocio): cache de la composición FHIR (TTL 300s).

## 2.10 `audit_db` — `audit-service` (M4)
```sql
CREATE TABLE audit_log (
    id            BIGSERIAL PRIMARY KEY,
    event_type    VARCHAR(100) NOT NULL,
    actor_id      UUID, payload JSONB NOT NULL,
    ai_confidence DECIMAL(4,3) NULL, ai_explainability JSONB NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);
-- Inmutabilidad a nivel de motor: el usuario de aplicación no puede alterar ni borrar
REVOKE UPDATE, DELETE ON audit_log FROM app_user;

-- Tabla separada para el estado de revisión del DPD (clase AuditoriaTrazabilidad.estadoRevision
-- del Apéndice A). Vive aparte de audit_log a propósito: revisarAuditoria() necesita poder
-- actualizar un estado, y audit_log es append-only por diseño (RNF-35, no repudio).
-- La referencia a audit_log.id es lógica, no un REFERENCES cruzado de constraint.
CREATE TABLE audit_reviews (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_log_id        BIGINT NOT NULL,          -- referencia lógica a audit_log.id
    estado_revision     VARCHAR(20) DEFAULT 'pendiente',  -- pendiente|revisado|observado
    revisado_por        UUID NULL,                -- delegado_dpd.id
    comentario          TEXT NULL,
    fecha_revision      TIMESTAMPTZ NULL,
    created_at          TIMESTAMPTZ DEFAULT now()
);
-- Esta tabla SÍ admite UPDATE (por el propio app_user) porque modela el ciclo de vida
-- de la revisión, no la evidencia inmutable en sí.
```

## 2.11 `admin_db` — `admin-integracion-service` (M4)
```sql
CREATE TABLE centers (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    type        VARCHAR(50),
    latitude    DECIMAL(9,6), longitude DECIMAL(9,6),
    status      VARCHAR(20) DEFAULT 'pending_validation'  -- pending_validation|validated|rejected
);

CREATE TABLE professionals (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    center_id   UUID REFERENCES centers(id),
    specialty   VARCHAR(100),
    available   BOOLEAN DEFAULT TRUE,
    current_load SMALLINT DEFAULT 0
);

CREATE TABLE devices (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id    UUID NOT NULL,
    device_type   VARCHAR(50),   -- ekg|oximeter|glucometer|...
    registered_by UUID NOT NULL, -- admin que lo vinculó
    active        BOOLEAN DEFAULT TRUE
);
```

## Sin schema propio
- `notification-service` — solo Redis (preferencias de canal + cola de reintentos, TTL 24h).
- `bff-service` — no persiste nada.

---

# 3. Referencia cruzada con el Diagrama de Clases (Apéndice A)

| Tabla | Clase del Apéndice A que cubre |
|---|---|
| `patients` | Usuario (parcial — perfil clínico) |
| `solicitudes` | SolicitudMedica |
| `vity_conversations`, `faq_entries` | (soporte de LLM/RAG, no son clases de dominio persistidas) |
| `vital_signs`, `monitoring_alerts` | DispositivoMonitoreo, Alerta (parcial) |
| `evaluaciones_riesgo` | EvaluacionRiesgo |
| `matchings` | AsignacionRecursos (parcial) |
| `teleconsults` | Teleconsulta |
| `emergency_cases` | EmergenciaMedica |
| `guias_primeros_auxilios` | GuiaPrimerosAuxilios |
| `clinical_cases` | HistoriaClinica + Caso (fusionadas en una sola tabla) |
| `expedientes_consolidados` | ExpedienteMedico |
| `audit_log` + `audit_reviews` | AuditoriaTrazabilidad (evidencia inmutable + estado de revisión separado) |
| `centers`, `professionals` | CentroMedico, ProfesionalSalud (parcial) |
| `devices` | DispositivoMonitoreo (registro administrativo) |

No cubiertas por ninguna tabla propia (son actores externos o roles RBAC, no persistencia propia): `LLM`, `RAG`, `Consorcio`, `EntidadExterna`, `DelegadoDPD`, `AdministradorSAMR`, `EnfermeroParamedico`.

---
*Ver también: `arch/system-design` (responsabilidades de cada servicio), `logic/core-services` (qué evento dispara cada escritura/lectura entre schemas).*

---

# 4. Bitácora de Decisiones Técnicas (v4.0 - Persistencia)

**Decisión Arquitectónica sobre el Desacoplamiento de `init-db.sh`:**
- Para mantener la infraestructura aislada y evitar el acoplamiento con los comandos del host, se decidió que el archivo `scripts/init-db.sh` actúe estrictamente como un **script nativo de inicialización de PostgreSQL**. 
- Es montado en `docker-entrypoint-initdb.d` y ejecutado automáticamente por el motor de BD en el primer inicio.
- **Responsabilidad Única del Script:** Crea las 11 bases de datos con codificación `UTF8` y define las tablas base (schemas) integrando explícitamente las reglas DDL del negocio (`UUID PRIMARY KEY DEFAULT gen_random_uuid()`, `JSONB`, `BYTEA`).
- **Inmutabilidad Asegurada:** Al definir el schema nativamente durante el `init-db.sh`, podemos aplicar de inmediato la instrucción `REVOKE UPDATE, DELETE ON audit_log FROM samr;` antes de que Django se conecte, garantizando la inmutabilidad de los registros de auditoría a nivel de motor.
- **Sincronización del Backend:** Los servicios en Python seguirán ejecutando sus propias rutinas de migración (`manage.py migrate --noinput`). Como el schema DDL ya estará creado por `init-db.sh` cumpliendo las expectativas del ORM, Django sincronizará el estado de forma transparente, manteniendo un enfoque Database-First seguro y agnóstico a la aplicación.

---

# 5. Guía de Despliegue Local e Integración con Supabase

## 5.1 Variables de Entorno (`.env`)

Asegúrate de contar con el archivo `.env` en la raíz del proyecto configurado con las credenciales del servidor PostgreSQL de Supabase y las claves de encriptación requeridas:

```env
DB_HOST=db.deqyvnvfmrqlxhcbkzuv.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=<PASSWORD_DE_SUPABASE>

RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/%2F
REDIS_URL=redis://redis:6379/0

SECRET_KEY=your-super-secret-key
PATIENT_DATA_KEY=wzd1e062k1A2WiEiHi8mBo52fy_jmDJKk8a2ZI11HLE=
```

## 5.2 Levantar la Infraestructura Docker Local

Debido a que el contenedor de RabbitMQ puede demorar en la inicialización completa durante el primer arranque y hacer fallar el healthcheck de Docker (`container samr-rabbitmq is unhealthy`), sigue este procedimiento para garantizar un despliegue sin bloqueos:

**Paso 1: Levantar los servicios sin evaluación estricta de dependencias**

Ejecuta el despliegue desacoplado de dependencias para que todos los microservicios backend, el BFF y Nginx inicien correctamente:

```bash
docker compose up -d --no-deps
```

> Nota: Si prefieres levantar servicios específicos de la API y el proxy:
> ```bash
> docker compose up -d --no-deps bff-service nginx
> ```

**Paso 2: Verificar el estado de los contenedores**

Consulta que los procesos estén en ejecución:

```bash
docker ps
```

## 5.3 Puertos y Accesos Locales

Los microservicios backend residen en la red interna de Docker (bridge network). Las peticiones deben realizarse a través del BFF o del Proxy Inverso:

- **Documentación Interactiva (Swagger BFF):** http://localhost:8000/docs
- **Endpoint de Salud del BFF:** http://localhost:8000/health
- **Gateway Nginx:** http://localhost
- **Gestión de RabbitMQ (Consola Admin):** http://localhost:15672 (Usuario/Pass: `guest` / `guest`)

## 5.4 Persistencia Multiesquema en Supabase

Los microservicios están enlazados a la instancia remota de Supabase. Antes de realizar pruebas de escritura o lectura, confirma que los siguientes esquemas aislados se encuentren creados y accesibles:

- `auth_db`
- `cierre_db`
- `emergency_db`
- `evaluacion_db`
- `admin_db`
- `audit_db`
- `solicitud_db`
- `patient_db`
