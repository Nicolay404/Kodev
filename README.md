# SAMR - Arquitectura de Sistema
## Rama `arch/system-design`

Este es el plan arquitectónico completo del sistema SAMR (Sistema de Atención Médica Remota).

### Cómo usar esta rama

1. **Contexto:** Lee `ARCHITECTURE.md` (mismo contenido en `AGENTS.md` para Antigravity)
2. **Agente:** La rama usa Antigravity IDE - el agente leerá `AGENTS.md` automáticamente en cada sesión
3. **Trabajo:** El arquitecto de software genera la estructura de carpetas, docker-compose.yml, nginx.conf, y los esqueletos de los 12 microservicios siguiendo el orden en `ARCHITECTURE.md` sección 5

### Dependencias de otras ramas

- `data/persistence-db` - Define el schema PostgreSQL de cada servicio (11 bases de datos independientes)
- `logic/core-services` - Define los eventos RabbitMQ y la comunicación entre servicios
- `sec/security-hardening` - Define la configuración de Nginx, JWT RS256 y RBAC
- `ui/frontend-app` - Depende de que el BFF y API Gateway estén listos
- `ux/design-prototypes` - Define lineamientos visuales y accesibilidad

### Orden de trabajo recomendado

1. `docker-compose.yml` + `nginx/samr.conf`
2. `scripts/init-db.sh` + `scripts/init-rabbitmq.sh`
3. `shared/events/{publisher,consumer}.py`
4. `auth-service/` completo
5. **M1:** patient-service, solicitud-service, monitoring-service
6. **M2:** evaluacion-service
7. **M3:** teleconsult-service, emergency-service, cierre-caso-service
8. **M4:** historial-interop-service, audit-service, admin-integracion-service
9. `notification-service/`
10. `frontend/` + `bff/bff-service/`

### Setup local (próximas fases)

```bash
bash scripts/setup.sh
docker compose up -d
```

---

**Última actualización:** $(date)
**Estado:** En construcción (fase: estructura base)

### Backend local - RabbitMQ

Para el vhost raíz de RabbitMQ se usa una ruta AMQP codificada, compatible tanto con Celery como con Pika:

```env
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/%2F
```

### Backend local - Pruebas

Cada microservicio incluye su configuración de pytest. Con el entorno levantado, una suite individual se ejecuta así:

```bash
docker compose exec auth-service python -m pytest -q
```

### Backend local - cifrado de datos de paciente

`patient-service` cifra la cédula con Fernet. El valor de desarrollo está en `.env.example`; en cualquier ambiente compartido debe reemplazarse:

```env
PATIENT_DATA_KEY=<clave-fernet-base64-de-32-bytes>
```

Los adaptadores backend del MVP se controlan sin acoplar el dominio a proveedores externos:

```env
AUTH_LOCK_MINUTES=10
REDIS_URL=redis://redis:6379/0
MVP_FAQ_CONFIDENCE_THRESHOLD=0.85
MVP_CONSORTIUM_OUTCOME=validated
```

`MVP_CONSORTIUM_OUTCOME` admite `validated`, `rejected` o `timeout` para probar los estados del flujo M2M.

La ingesta IoT MVP usa `MVP_DEVICE_SERVICE_TOKEN` y reglas configurables en `MVP_VITAL_THRESHOLDS`. Estos umbrales sirven solo para pruebas técnicas y deben sustituirse por reglas clínicas validadas.

La evaluación MVP usa `MVP_DEFAULT_RISK_LEVEL`, `MVP_CRITICAL_TERMS` y `MVP_HIGH_TERMS`. Las listas vienen vacías deliberadamente: deben configurarse solo con criterios aprobados para la demostración.

`MVP_FIRST_AID_GUIDE` define el mensaje de seguridad del simulador de emergencias. No debe reemplazarse por instrucciones clínicas sin aprobación profesional.

`historial-interop-service` verifica consentimiento mediante `PATIENT_SERVICE_URL` y conserva Bundles FHIR durante 300 segundos en Redis.

`MVP_CENTER_VALIDATION_OUTCOME` permite simular `validated` o `rejected` en la validación M2M de centros.

`admin-integracion-service` incluye un worker Celery para ejecutar esa validación asíncrona usando RabbitMQ.

El BFF usa `BFF_ALLOWED_ORIGINS` y `VERIFY_GATEWAY_TLS`; la verificación TLS solo se desactiva en el certificado autofirmado local.

Las notificaciones del MVP usan `MVP_NOTIFICATION_BACKEND=log`; un proceso `notification-consumer` recibe eventos y el worker Celery ejecuta el adaptador simulado.

### Backend local - arranque reproducible y procesos asíncronos

Desde `samr/`, el entorno completo se construye y arranca con:

```bash
docker compose up -d --build
```

En un volumen PostgreSQL nuevo, `scripts/init-db.sh` crea automáticamente las 11 bases y cada API ejecuta sus migraciones antes de abrir el puerto. Los consumidores RabbitMQ declaran de forma idempotente exchange, cola quorum y DLQ; no se requiere inicialización manual para el flujo MVP.

Compose inicia consumidores separados y workers Celery con cola propia para solicitud, evaluación, historial, auditoría, administración y notificaciones. La concurrencia local es 1 por worker para limitar recursos del MVP.

Dependencias backend añadidas por estos módulos: `celery==5.3.6` en `admin-integracion-service`, y `redis==5.0.3` en `solicitud-service` e `historial-interop-service`. Docker las instala desde cada `requirements.txt`.

## Backend - bandeja de notificaciones del MVP

`notification-service` expone `GET /api/notifications/` y `PATCH /api/notifications/{id}/read/` a través de Nginx. La bandeja usa únicamente Redis, conserva hasta 100 entradas por usuario durante 24 horas y requiere un JWT access emitido por `samr-auth-service`.

El proceso HTTP, `notification-consumer` y `notification-worker` se ejecutan por separado. El backend externo continúa simulado con `MVP_NOTIFICATION_BACKEND=log`; la bandeja Redis permite probar el recorrido completo sin presentar el log como un envío FCM real.

## Backend - ejecución con PostgreSQL de Supabase

El backend admite Supabase como PostgreSQL remoto sin usar el SDK de Supabase ni Supabase Auth. `auth-service` continúa siendo el único responsable de validar credenciales y firmar JWT; la persistencia se realiza en la base indicada por `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`.

La arquitectura mantiene los once dominios aislados mediante schemas PostgreSQL (`auth_db`, `patient_db`, `solicitud_db`, `monitoring_db`, `evaluacion_db`, `teleconsult_db`, `emergency_db`, `cierre_db`, `historial_db`, `audit_db` y `admin_db`). La conexión exige SSL y cada servicio fija su propio `search_path`; no existen consultas cruzadas entre schemas.

Desde `samr/`, con las credenciales reales exclusivamente en `.env`, el modo Supabase se inicia con:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.supabase.yml up -d --build
```

`supabase-init` crea los schemas de forma idempotente y las migraciones usan `--fake-initial` para adoptar tablas canónicas preexistentes sin recrearlas. La red Compose habilita IPv6 para el endpoint directo de Supabase. El modo PostgreSQL local original permanece disponible ejecutando únicamente `docker compose up -d --build`.

`.env` está excluido de Git. Nunca deben copiarse contraseñas, hosts privados ni claves reales a `.env.example`, README, ONBOARDING o commits.

## Backend - usuarios demo en Supabase

Las siguientes cuentas existentes usan la contraseña común `Demo1234` exclusivamente para probar el MVP:

| Usuario | Rol backend | Contraseña |
|---|---|---|
| `paciente.juan@gmail.com` | `patient` | `Demo1234` |
| `paciente.maria@gmail.com` | `patient` | `Demo1234` |
| `user@prueba1.com` | `patient` | `Demo1234` |
| `dr.mendoza@samr-salud.gob.ec` | `professional` | `Demo1234` |
| `admin.sistema@samr-salud.gob.ec` | `system_admin` | `Demo1234` |
| `delegado.dpd@samr-salud.gob.ec` | `dpd_delegate` | `Demo1234` |

Para restablecerlas nuevamente en el modo Supabase, ejecuta desde `samr/`:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.supabase.yml run --rm --no-deps auth-service python manage.py reset_demo_passwords --password Demo1234
```

El comando no crea usuarios: exige que existan las seis cuentas, reemplaza sus hashes con el formato Django, limpia bloqueos y corrige el rol legado `pacient` de `user@prueba1.com` a `patient`. Para usar otra clave temporal, sustituye el valor de `--password`; debe tener al menos ocho caracteres, una letra y un número.

Estas credenciales son públicas dentro del repositorio y no deben reutilizarse en producción ni en cuentas reales. Las credenciales de conexión a Supabase continúan exclusivamente en el `.env` ignorado por Git.
