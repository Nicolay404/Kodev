# SAMR — Arquitectura de Sistema
## Rama `arch/system-design`

> Patrones arquitectónicos, topología, límites de microservicios por módulo, y estructura de despliegue. Para el detalle de base de datos ver `data/persistence-db`; para eventos/RabbitMQ ver `logic/core-services`; para seguridad ver `sec/security-hardening`.

---

# 1. Los 4 módulos de referencia y por qué se reorganizaron los servicios

Fuente de verdad: ESP-HS-SAMR v1.0.5 (Historias de Usuario) y el Diagrama de Clases (Apéndice A).

| Módulo | Caso de uso | RF que agrupa | Actores (Apéndice A) |
|---|---|---|---|
| **M1 — Módulo de Solicitud** | CU-001 | RF-01 a RF-07 | Usuario (Paciente/Familiar), LLM, RAG, Consorcio, DispositivoMonitoreo |
| **M2 — Módulo de Evaluación y Asignación** | CU-002 | RF-08 a RF-12 | LLM, RAG, ProfesionalSalud, CentroMedico |
| **M3 — Módulo de Atención** | CU-003 | RF-13 a RF-15 | ProfesionalSalud, Paciente, LLM, RAG, EnfermeroParamedico, Familiar |
| **M4 — Módulo de Integración e Interoperabilidad Clínica** | CU-004 | RF-16 a RF-20 | AdministradorSAMR, Usuario, EntidadExterna (IESS/MSP), Consorcio, DelegadoDPD |

**Principio rector:** un microservicio pertenece a un solo módulo de negocio (M1–M4). Ningún servicio mezcla responsabilidades de dos módulos distintos (excepto los explícitamente transversales: `auth-service`, `notification-service`, `bff-service`).

## Problemas de una versión anterior (ya corregidos aquí)

| Servicio (versión anterior) | Módulos que mezclaba | Corrección aplicada |
|---|---|---|
| `vity-ai-service` | M1 (chat/FAQ) + M2 (evaluación de riesgo) | Dividido: chat/FAQ → `solicitud-service` (M1); evaluación de riesgo → `evaluacion-service` (M2) |
| `emergency-service` | M1 (validación) + M2 (matching) + M3 (emergencias) | Validación → `solicitud-service` (M1); matching/asignación → `evaluacion-service` (M2); solo emergencias queda en `emergency-service` (M3) |
| `center-service` | M2 (lectura de catálogo) + M4 (registro/validación) | Lectura → `evaluacion-service` (M2, cache de solo lectura); registro/validación → `admin-integracion-service` (M4) |
| `monitoring-service` | M1 (ingesta IoT) + M4 (registro de dispositivos) | Ingesta/anomalías se queda en `monitoring-service` (M1); registro de dispositivos → `admin-integracion-service` (M4) |
| `followup-service` + `interop-service` | M3 + M4 separados sin necesidad | Cierre de caso → `cierre-caso-service` (M3); historial consolidado + FHIR → `historial-interop-service` (M4) |
| `bff-service` | — (mal ubicado en la topología) | Reposicionado: Frontend → BFF → API Gateway (antes vivía detrás del Gateway) |

---

# 2. Patrones Arquitectónicos Aplicados

| Patrón | Descripción | Aplicación en SAMR |
|---|---|---|
| **Database-per-Service** | Cada servicio posee su propio schema/base de datos; ningún JOIN entre schemas | 11 servicios con base de datos propia + 2 sin schema PostgreSQL propio (`notification-service` usa solo Redis, `bff-service` no persiste nada) |
| **API Gateway** | Punto único de entrada para todo el tráfico que llega a los microservicios | Nginx: routing por prefijo, rate limiting, WAF, TLS, verificación JWT previa (ver `sec/security-hardening`) |
| **Backend For Frontend (BFF), reubicado** | Capa de agregación **delante** del API Gateway, exclusiva del cliente web | `bff-service` recibe las peticiones del Frontend, agrega `patient + evaluacion + monitoring + atención` en una sola respuesta, y es quien llama al API Gateway — nunca al revés |
| **Event-Driven / Coreografía** | Los servicios reaccionan a eventos publicados por otros, sin orquestador central | RabbitMQ (ver `logic/core-services`); ningún servicio le "ordena" a otro qué hacer |
| **Saga Coreografiada** | Transacción distribuida sin coordinador central | `solicitud.creada (M1) → riesgo.evaluado (M2) → recursos.asignados (M2) → atencion.iniciada (M3) → caso.cerrado (M3) → historial.consolidado (M4)` |
| **Un servicio, un módulo** | Ningún microservicio implementa RF de dos módulos distintos | Ver sección 1 y el desglose completo en la sección 4 |
| **Polyglot Persistence (mínimo necesario)** | Un motor por tipo de dato, sin motores redundantes | PostgreSQL para todo dato persistente; Redis solo para cache/WebSocket; RabbitMQ solo para mensajería |
| **Zero Trust interno** | Ningún servicio confía en otro por estar en la misma red | Ver `sec/security-hardening` |

---

# 3. Topología de Red (BFF reubicado)

```
╔══════════════════════════════════════════════════════════════════════╗
║        PACIENTES · PROFESIONALES · ADMINISTRADORES (Frontend React)   ║
╚═════════════════════════════════╦════════════════════════════════════╝
                                   │ HTTPS — el Frontend SOLO conoce la URL del BFF
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║  BFF-SERVICE — Backend For Frontend                                   ║
║  Agrega patient + evaluacion + monitoring + atencion para el          ║
║  dashboard en una sola respuesta. Sin base de datos propia.           ║
║  Es cliente del API Gateway, nunca al revés.                          ║
╚═════════════════════════════════╦════════════════════════════════════╝
                                   │ HTTPS :443 (TLS 1.3) interno
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║  NGINX — API GATEWAY                                                  ║
║  Rate limiting por zona · WAF regex · Headers de seguridad            ║
║  Verificación JWT (clave pública RS256) antes de rutear                ║
║  También expuesto directo a: apps móviles, dispositivos IoT           ║
╚═════════════╦══════════════════════════════════════════════════════════╝
              │ Red Docker privada (sin puertos expuestos al exterior)
              │
   ── Transversales ──────────────────────────────────────────────────
   ┌────────────┐                              ┌──────────────────┐
   │auth-service│                              │notification-     │
   │:8001       │                              │service :8012     │
   │PG:auth_db  │                              │Redis only + FCM  │
   └────────────┘                              └──────────────────┘

   ── M1 · Módulo de Solicitud (CU-001 · RF-01 a RF-07) ───────────────
   ┌──────────────┐┌────────────────┐┌──────────────────┐
   │patient-      ││solicitud-       ││monitoring-        │
   │service :8002 ││service :8003    ││service :8004      │
   │PG:patient_db ││PG:solicitud_db  ││PG+Redis:monitoring│
   │              ││(vity chat+RAG)  ││(IoT + WebSocket)  │
   └──────────────┘└────────────────┘└──────────────────┘

   ── M2 · Módulo de Evaluación y Asignación (CU-002 · RF-08 a RF-12) ──
   ┌───────────────────────┐
   │evaluacion-service :8005│
   │PG:evaluacion_db        │
   │(riesgo IA + matching + │
   │ asignación de recursos)│
   └───────────────────────┘

   ── M3 · Módulo de Atención (CU-003 · RF-13 a RF-15) ─────────────────
   ┌──────────────┐┌───────────────┐┌────────────────────┐
   │teleconsult-  ││emergency-      ││cierre-caso-service  │
   │service :8006 ││service :8007   ││:8008                │
   │PG+Redis+WebRTC│PG:emergency_db││PG:cierre_db         │
   └──────────────┘└───────────────┘└────────────────────┘

   ── M4 · Módulo de Integración e Interoperabilidad Clínica ──────────
   ── (CU-004 · RF-16 a RF-20) ────────────────────────────────────────
   ┌───────────────────┐┌────────────┐┌──────────────────────┐
   │historial-interop-  ││audit-      ││admin-integracion-     │
   │service :8009       ││service     ││service :8011          │
   │PG:historial_db     ││:8010       ││PG:admin_db            │
   │(expediente + FHIR) ││PG (append) ││(centros + dispositivos)│
   └───────────────────┘└────────────┘└──────────────────────┘

╔══════════════════════════════════════════════════════════════════════╗
║  RABBITMQ 3.13 — Event Bus (exchange topic `samr.events`)             ║
║  + broker de Celery (una sola tecnología de mensajería)                ║
╚══════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════╗
║  REDIS 7.2 — Cache de lecturas + Channel Layer WebSocket (solamente)  ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Por qué el BFF va antes del Gateway y no detrás:** el BFF no es "un microservicio de negocio más" — no implementa ningún RF por sí mismo, solo agrega respuestas de otros servicios para reducir las llamadas paralelas que el dashboard tendría que hacer. Colocándolo delante, el contrato queda más limpio: *el Frontend solo habla con el BFF; el BFF solo habla con el Gateway; el Gateway es el único que conoce la topología interna de los 12 microservicios de negocio.*

---

# 4. Desglose de Microservicios (responsabilidades y endpoints, organizado por módulo)

> El esquema SQL de cada tabla vive en la rama `data/persistence-db`. Aquí solo se documenta responsabilidad, endpoints y eventos (el detalle de eventos está ampliado en `logic/core-services`).

## 4.0 Servicios Transversales

### `auth-service` :8001 — Autenticación e Identidad
**Responsabilidad única:** ciclo de vida de la identidad — registro, login, emisión/revocación de JWT (RS256), bloqueo por intentos fallidos, RBAC. Es el único servicio con la clave privada RSA.

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/auth/register/` | POST | Pública | RF-01 |
| `/api/auth/login/` | POST | Pública (rate-limited 5/min) | RF-01, RNF-01 |
| `/api/auth/token/refresh/` | POST | Refresh token | RNF-01 |
| `/api/auth/me/` | GET | JWT | RF-01 |

### `notification-service` :8012 — Notificaciones Multi-Canal
**Responsabilidad única:** despacho de notificaciones push (FCM). Servicio puramente reactivo, sin endpoints de negocio.

### `bff-service` — Backend For Frontend
**Responsabilidad única:** agregar `patient + evaluacion + monitoring + cierre-caso` en una sola respuesta para el dashboard. Reposicionado entre el Frontend y el Gateway (sección 3).

| Endpoint (directo al Frontend, no vía Nginx) | Método | Auth |
|---|---|---|
| `/dashboard/` | GET | JWT (propaga a servicios internos a través del Gateway) |

## 4.1 M1 — Módulo de Solicitud (CU-001 · RF-01 a RF-07)

### `patient-service` :8002 — Perfil Clínico del Paciente
**Responsabilidad única:** datos demográficos, alergias, condiciones crónicas, geolocalización, consentimientos LOPDP.

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/patients/me/` | GET/PATCH | JWT (paciente) | RF-01 |
| `/api/patients/{id}/summary/` | GET | X-Service-Token (M2M) | RF-08, RF-11 |

### `solicitud-service` :8003 — Bot Conversacional, Registro y Validación de Solicitud
**Responsabilidad única:** conversación con el paciente (RF-02, RF-07), registro de la solicitud médica (RF-03) y validación M2M con el Consorcio (RF-04).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/solicitud/chat/` | POST | JWT (paciente) | RF-02, RF-07 |
| `/api/solicitud/faq/` | GET/POST/PATCH | Admin JWT (POST/PATCH) | RF-07, RNF-12 |
| `/api/solicitud/` | POST | JWT (paciente) | RF-03 |
| `/api/solicitud/conversations/{id}/` | DELETE | JWT (dueño) | LOPDP — derecho al olvido |

**Flujo de validación M2M con el Consorcio (RF-04):**
```
1. Usuario/Dispositivo genera la solicitud → estado='pendiente', publica "solicitud.creada"
2. solicitud-service llama de forma asíncrona (Celery) al Consorcio para validar datos obligatorios
3. Si no hay respuesta en ≤ 5s o hay error → estado='pendiente_reintento' (RNF-07)
4. Si valida → estado='validada', publica "solicitud.validada" (consumido por evaluacion-service)
   Si rechaza → estado='rechazada'
```

### `monitoring-service` :8004 — IoT, Signos Vitales y Detección de Anomalías
**Responsabilidad única:** ingesta de datos IoT (RF-05), detección de anomalías (RF-06), WebSocket en tiempo real. No incluye registro administrativo de dispositivos (eso es `admin-integracion-service`, M4).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/monitoring/iot-events/` | POST | Device token | RF-05, RNF-08, RNF-09 |
| `/api/monitoring/alerts/` | GET | Medical/Admin JWT | RF-06 |
| `ws/monitoring/{patient_id}/` | WebSocket | JWT (query param) | RF-06, RNF-10 |

## 4.2 M2 — Módulo de Evaluación y Asignación (CU-002 · RF-08 a RF-12)

### `evaluacion-service` :8005 — Evaluación de Riesgo, Matching y Asignación de Recursos
**Responsabilidad única:** todo el ciclo de CU-002 en un solo servicio: evaluación de riesgo con IA (RF-08), recomendaciones RAG (RF-09), búsqueda de centros disponibles — solo lectura (RF-10), matching (RF-11), asignación de recursos + notificación (RF-12).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/evaluacion/riesgo/{solicitud_id}/` | GET | JWT | RF-08, RF-09 |
| `/api/evaluacion/centros-disponibles/` | GET | X-Service-Token | RF-10 |
| `/api/evaluacion/matching/{evaluacion_id}/` | POST | Medical/Admin JWT | RF-11, RF-12 |

## 4.3 M3 — Módulo de Atención (CU-003 · RF-13 a RF-15)

### `teleconsult-service` :8006 — Teleconsulta con Señalización WebRTC
**Responsabilidad única:** sesión de teleconsulta (RF-13) — creación de sala, señalización WebRTC, chat, notas médicas.

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/teleconsult/` | POST | Medical/Admin JWT | RF-13 |
| `ws/teleconsult/{room_token}/` | WebSocket (señalización SDP/ICE) | JWT (query param) | RF-13 |

### `emergency-service` :8007 — Gestión de Emergencias Médicas
**Responsabilidad única:** exclusivamente RF-14 — protocolo de emergencias, guía de primeros auxilios, despacho de ambulancia. Ya no hace matching (eso es M2) ni valida solicitudes (eso es M1).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/emergencies/` | POST/GET | JWT | RF-14 |
| `/api/emergencies/{id}/dispatch/` | POST | Admin/Medical JWT | RF-14 |

### `cierre-caso-service` :8008 — Actualización de Historial y Cierre del Caso
**Responsabilidad única:** actualización del historial clínico durante la atención y cierre operativo del caso (RF-15), verificación de integridad antes de cerrar (RNF-28).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/cierre-caso/{id}/close/` | POST | Medical JWT | RF-15, RNF-28 |
| `/api/cierre-caso/{id}/verify/` | GET | Medical/Admin JWT | RNF-28 |

## 4.4 M4 — Módulo de Integración e Interoperabilidad Clínica (CU-004 · RF-16 a RF-20)

### `historial-interop-service` :8009 — Historial Clínico Consolidado e Interoperabilidad FHIR
**Responsabilidad única:** expediente clínico consolidado por paciente (RF-16) y exposición en formato FHIR R4 a MSP/IESS/Consorcio (RF-17).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/historial/{patient_id}/` | GET | Medical/Patient JWT | RF-16 |
| `/api/history/fhir/{patient_id}/` | GET | Medical/Patient JWT + consentimiento | RF-17, RNF-32, RNF-34 |

### `audit-service` :8010 — Auditoría Inmutable y Auditoría DPD
**Responsabilidad única:** registro append-only de decisiones de IA (RF-18) y auditoría DPD (RF-20).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/audit/decisions/` | GET | JWT rol `dpd_delegate` | RF-20, RNF-38 |
| `/api/audit/decisions/{audit_log_id}/review/` | PATCH | JWT rol `dpd_delegate` | RF-20 |

### `admin-integracion-service` :8011 — Administración del Sistema (Centros y Dispositivos)
**Responsabilidad única:** RF-19 completo — registro y validación M2M con el Consorcio de nuevos centros médicos, y registro/vinculación de dispositivos IoT.

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/admin/centers/register/` | POST | Admin JWT (`system_admin`) | RF-19 |
| `/api/admin/centers/available/` | GET | X-Service-Token (leído por `evaluacion-service`) | RF-10 |
| `/api/admin/devices/register/` | POST | Admin JWT (`system_admin`) | RF-19 |

---

# 5. Estructura de Carpetas y Despliegue

**Estructura de carpetas obligatoria:**
```
samr/
├── frontend/                       ← React SPA — solo conoce la URL del BFF
├── bff/
│   └── bff-service/                ← delante del Gateway (ver sección 3)
├── nginx/samr.conf                 ← API Gateway (ver sec/security-hardening)
├── services/                       ← 12 microservicios de negocio, agrupados por módulo
│   ├── auth-service/                       (transversal)
│   ├── notification-service/               (transversal)
│   ├── patient-service/                    (M1)
│   ├── solicitud-service/                  (M1)
│   ├── monitoring-service/                 (M1)
│   ├── evaluacion-service/                 (M2)
│   ├── teleconsult-service/                (M3)
│   ├── emergency-service/                  (M3)
│   ├── cierre-caso-service/                (M3)
│   ├── historial-interop-service/          (M4)
│   ├── audit-service/                      (M4)
│   └── admin-integracion-service/          (M4)
├── shared/
│   ├── events/publisher.py        ← idéntico en los 12 servicios (ver logic/core-services)
│   └── events/consumer.py
├── event-schemas/                 ← 1 archivo JSON Schema por routing key
├── scripts/
│   ├── init-db.sh                 ← crea los 11 schemas PostgreSQL (ver data/persistence-db)
│   └── init-rabbitmq.sh           ← declara exchange, colas y DLX
├── docker-compose.yml
└── .env.example
```

**Estructura interna por cada servicio Django:**
```
{service}/
├── Dockerfile              ← multi-stage: builder + final (python:3.12-slim, usuario no-root)
├── requirements.txt
├── manage.py
├── config/
│   ├── settings/{base,development,production}.py
│   ├── urls.py
│   └── asgi.py             ← solo con Channels en monitoring-service y teleconsult-service
├── apps/{dominio}/
│   ├── models.py, serializers.py, views.py, urls.py, permissions.py, services.py
├── consumers/              ← solo monitoring-service y teleconsult-service
├── events/{publisher,consumer}.py
├── tasks/                  ← solo servicios con Celery
└── tests/
```

**Orquestación local (`docker-compose.yml`):**
```yaml
services:
  postgres:
    image: postgres:16
    environment: [POSTGRES_USER=samr, POSTGRES_PASSWORD=${DB_PASSWORD}]
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7.2-alpine

  rabbitmq:
    image: rabbitmq:3.13-management   # incluye UI web en :15672 para depurar en la demostración
    ports: ["15672:15672"]

  nginx:
    image: nginx:1.26-alpine
    ports: ["443:443", "80:80"]
    volumes: ["./nginx/samr.conf:/etc/nginx/conf.d/default.conf", "./ssl:/etc/nginx/ssl"]
    depends_on: [auth-service, patient-service, solicitud-service, monitoring-service,
                 evaluacion-service, teleconsult-service, emergency-service, cierre-caso-service,
                 historial-interop-service, audit-service, admin-integracion-service,
                 notification-service]

  bff-service:
    build: ./bff/bff-service
    ports: ["8000:8000"]        # único servicio de aplicación expuesto al Frontend además de Nginx
    depends_on: [nginx]
    environment:
      - API_GATEWAY_URL=https://nginx

  auth-service:
    build: ./services/auth-service
    environment:
      - DB_NAME=auth_db
      - RABBITMQ_URL=${RABBITMQ_URL}
      - JWT_PRIVATE_KEY_PATH=/keys/private.pem   # solo este servicio monta la clave privada
    volumes: ["./keys:/keys:ro"]
  # (resto de servicios: mismo patrón, sin JWT_PRIVATE_KEY_PATH — solo public.pem)

volumes: [pgdata]
```

**Orden de generación de código recomendado:**
1. `docker-compose.yml` + `nginx/samr.conf`
2. `scripts/init-db.sh` + `scripts/init-rabbitmq.sh`
3. `shared/events/{publisher,consumer}.py`
4. `auth-service/` completo (genera par de claves RSA)
5. **M1:** `patient-service/`, `solicitud-service/`, `monitoring-service/`
6. **M2:** `evaluacion-service/`
7. **M3:** `teleconsult-service/`, `emergency-service/`, `cierre-caso-service/`
8. **M4:** `historial-interop-service/`, `audit-service/`, `admin-integracion-service/`
9. `notification-service/`
10. `frontend/` + `bff/bff-service/`

**Reglas absolutas :**
1. Ningún servicio importa código de otro servicio — aislamiento total.
2. Ningún microservicio implementa RF de más de un módulo (M1–M4).
3. JWT: solo `auth-service` firma (RS256); los demás solo verifican.
4. Un schema PostgreSQL por servicio, sin Foreign Keys entre schemas.
5. Comunicación entre servicios: RabbitMQ para eventos; `X-Service-Token` para M2M puntual.
6. El `bff-service` es el único que llama al API Gateway usando el JWT del usuario propagado.
7. Docker multi-stage, usuario no-root, `HEALTHCHECK` incluido.
8. Celery: broker = RabbitMQ; `autodiscover_tasks(['tasks'])`.
9. Un test mínimo por endpoint (`APIClient` de DRF).
10. `README.md` por servicio con instalación y ejecución local.
11. Generar primero la estructura de carpetas completa antes de escribir código.

---
*Ver también: `data/persistence-db` (esquemas SQL), `logic/core-services` (eventos y comunicación), `sec/security-hardening` (Nginx, JWT, RBAC), `ui/frontend-app`, `ux/design-prototypes`.*

---

# Registro de trabajo de agentes

## 2026-07-20 — Documentación operativa final del backend

- Se anexó a `README.md` y `samr/ONBOARDING.md` el arranque automático vigente, la topología de workers/consumidores y las dependencias nuevas (`celery`/`redis`).
- Se preservaron las secciones preexistentes; la aclaración del backend se añadió al final conforme a la regla de integridad documental.

## 2026-07-20 — Verificación de emisor JWT en BFF

- El BFF ahora valida explícitamente `iss=samr-auth-service`, además de firma RS256, expiración y tipo `access`.
- Se actualizó el fixture BFF para representar el mismo contrato de token que emite `auth-service`.

## 2026-07-20 — Smoke test HTTPS y BFF

- Se verificó registro y login reales a través de Nginx/TLS con el usuario sintético `mvp-smoke@samr.local`; el registro público ignoró escalamiento y creó rol `patient`, y el login emitió access/refresh RS256.
- El JWT real fue propagado por el BFF al Gateway y produjo las cuatro claves del contrato: `patient`, `evaluacion`, `monitoring`, `atencion`.
- Para el usuario sin perfil, `patient` devuelve 404; `evaluacion` y `atencion` listas vacías; `monitoring` devuelve 403 porque el único endpoint documentado de alertas exige rol Medical/Admin. No se ampliaron permisos fuera de los documentos.
- Se reinició Nginx después de recrear contenedores para renovar la resolución DNS de sus upstreams en el smoke test local.

## 2026-07-20 — Smoke test de saga coreografiada

- Se publicó en el clúster real el evento sintético `solicitud.validada` con ID `7bd0957f-7c36-41ee-aca6-0a72126cc07b`.
- `evaluacion-service` consumió el evento mediante RabbitMQ, su worker aislado persistió la evaluación de la solicitud sintética `55555555-5555-4555-8555-555555555555` con nivel MVP `medio` y publicó `riesgo.evaluado` y `ai.decision_logged`.
- `audit-service` consumió y persistió los tres eventos (`solicitud.validada`, `riesgo.evaluado`, `ai.decision_logged`), comprobando la comunicación entre M1, M2 y M4.
- No se activó emergencia porque la regla simulada no clasificó el caso como `critico`; no se modificaron umbrales clínicos para forzar el resultado.

## 2026-07-20 — Aplicación Celery activa en procesos Django

- La prueba de saga confirmó que los eventos llegaban a RabbitMQ, pero los consumidores usaban la aplicación Celery global al invocar `.delay()` y agotaban tres reintentos hacia la DLQ.
- Los seis servicios asíncronos exponen ahora `celery_app` desde `config/__init__.py`, por lo que vistas, comandos y consumidores usan el broker y la cola aislada definidos por su servicio.

## 2026-07-20 — Registro de tareas y recursos Celery del MVP

- Se registraron explícitamente los módulos de tareas de los seis workers; la autodetección genérica no importaba archivos con nombres de dominio como `procesar_solicitud.py`.
- Se fijó concurrencia 1 por worker para el entorno MVP local, reduciendo el consumo de procesos sin cambiar la separación de colas ni impedir escalar el valor en despliegues futuros.
- Se verificaron los nombres exportados de cada tarea, incluido `validate_with_consortium` para la simulación M2M.
- La verificación de clúster ajustó el registro a `app.conf.imports`: Celery importa cada módulo después de `django.setup()`, evitando `AppRegistryNotReady` en tareas que usan modelos.

## 2026-07-20 — Confirmación correcta de publicación RabbitMQ

- La prueba de saga real detectó y corrigió una interpretación incorrecta del retorno de `BlockingChannel.basic_publish`.
- Con publisher confirms activo, Pika comunica NACK o mensaje no enrutable mediante excepción; ya no se trata el retorno `None` de un ACK válido como error.
- La corrección se replicó en las 11 copias aisladas del publicador y en la referencia de `shared/events`.

## 2026-07-20 — Aislamiento de colas Celery

- Se asignó una cola, exchange y routing key Celery propios a solicitud, evaluación, historial, auditoría, administración y notificaciones.
- Esto impide que un worker consuma o descarte tareas pertenecientes a otro microservicio mientras todos comparten RabbitMQ como broker único.
- Se sincronizó el catálogo configurado de eventos de notificación con los bindings realmente consumidos por el MVP.

## 2026-07-20 — Inicialización ASGI para WebSocket

- Se corrigió el orden de arranque ASGI de `monitoring-service` y `teleconsult-service`: Django carga sus settings y registro de aplicaciones antes de importar consumidores que usan modelos.
- La corrección elimina el ciclo de reinicio observado al validar teleconsulta en el clúster real.

## 2026-07-20 — Cola y DLQ de notificaciones

- El consumidor de notificaciones ahora valida el sobre v1.0 y declara su exchange, cola quorum, límite de tres entregas y DLQ aislada de forma idempotente.
- Esta declaración automática permite levantar el MVP desde cero sin depender de una ejecución manual previa del script RabbitMQ.

## 2026-07-20 — Arranque reproducible de PostgreSQL y migraciones

- Se convirtió `scripts/init-db.sh` en un inicializador idempotente compatible con `/docker-entrypoint-initdb.d`, que crea exactamente las 11 bases documentadas.
- PostgreSQL monta el inicializador en Docker Compose y cada API persistente aplica sus migraciones antes de iniciar Daphne/Gunicorn, reintentando mientras la base termina de arrancar.
- Los procesos Django usan `restart: on-failure` para recuperarse de carreras de arranque de PostgreSQL o RabbitMQ sin introducir otro orquestador.

## 2026-07-20 — Corrección del adaptador de notificaciones MVP

- El adaptador de notificaciones lee `MVP_NOTIFICATION_BACKEND` directamente del entorno para poder ejecutarse tanto dentro de Celery/Django como en pruebas unitarias aisladas.
- Se mantiene `log` como único backend simulado permitido; cualquier valor no configurado falla explícitamente y no simula un envío real.

## 2026-07-20 — Procesos asíncronos del MVP

- Se declararon en Docker Compose los consumidores RabbitMQ separados de los servidores HTTP para M1, M2, M3, M4 y notificaciones.
- Se declararon workers Celery separados para validación de solicitudes, evaluación, consolidación FHIR, auditoría y validación de centros; RabbitMQ continúa siendo el único broker.
- Se completó la configuración Celery de `admin-integracion-service` con serialización JSON y confirmación tardía de tareas.

## 2026-07-20 — Trazabilidad HTTP y validación de contenido

- Se activó en los 12 servicios Django el middleware común que propaga o genera `X-Request-ID`.
- Las operaciones con cuerpo rechazan tipos distintos de `application/json` y `application/fhir+json` con HTTP 415, de acuerdo con el contrato HTTP del backend.

## 2026-07-20 — Contratos versionados del bus de eventos

- Se creó `samr/event-schemas/` con el sobre común v1.0 y un JSON Schema por cada routing key publicada por el MVP.
- Los contratos fijan identificadores, tipo, origen, fecha, versión y campos mínimos del payload sin acoplar los servicios entre sí.

## 2026-07-20 — Worker de validación externa MVP

- Se añadió la configuración Celery de `admin-integracion-service` para ejecutar de forma asíncrona el adaptador simulado de validación de centros médicos.
- El adaptador permanece desacoplado por variable de entorno para que la simulación del Consorcio pueda sustituirse posteriormente por una integración real sin cambiar el contrato del endpoint.

## 2026-07-19 — Preparación del ambiente local (`logic/core-services`)

- Se verificó que la rama activa es `logic/core-services` y que el árbol de trabajo estaba limpio al iniciar.
- Se instaló Docker Desktop 4.82.0 (Docker Engine CLI 29.6.1 y Docker Compose v5.3.0).
- Se habilitaron las características de Windows `Microsoft-Windows-Subsystem-Linux` y `VirtualMachinePlatform`; Windows requiere reinicio antes de iniciar el motor de Docker.
- Se creó `samr/.env` a partir de los valores de desarrollo ya definidos en `samr/.env.example`; el archivo permanece excluido de Git.
- Se generó el par de claves RSA de desarrollo en `samr/keys/` mediante el script existente de `auth-service`, y se excluyó ese directorio de Git para impedir que la clave privada se versionara.
- Se validó la sintaxis de todo el código Python de `samr/` mediante `compileall` (sin errores) y se añadieron exclusiones para artefactos locales `__pycache__/` y `*.py[cod]`.
- Tras iniciar Docker, se construyeron las 13 imágenes propias y se levantaron los 17 contenedores definidos por Compose.
- Se crearon de forma idempotente las 11 bases PostgreSQL definidas por el patrón Database-per-Service.
- Se generó una migración inicial por cada app de dominio (11 en total) exclusivamente desde los modelos existentes, sin agregar ni alterar campos o relaciones de negocio.
- Se implementó el comando Django `health` que ya era invocado por los Dockerfiles: valida PostgreSQL en los 11 servicios persistentes y RabbitMQ en `notification-service`.
- Se montó `public.pem` en modo solo lectura para todos los servicios verificadores y el BFF, manteniendo `private.pem` montada exclusivamente en `auth-service`; también se retiró la clave Compose `version` obsoleta.
- Se corrigió `RABBITMQ_URL` para codificar el vhost raíz como `%2F`, requerido por Pika y compatible con Celery, y se documentó el valor en README/ONBOARDING.
- Se fijó `eol=lf` para scripts Bash mediante `samr/.gitattributes`, evitando errores de ejecución Linux causados por finales CRLF de Windows.
- Se añadió configuración `pytest.ini` por servicio (`DJANGO_SETTINGS_MODULE` para Django y `pythonpath` para BFF) y se documentó el comando de pruebas backend.
- Se normalizó la respuesta de los autenticadores Bearer, M2M y de dispositivo agregando su encabezado `WWW-Authenticate`, para que DRF responda HTTP 401 cuando faltan credenciales.
- Se marcó `patient_id` como campo de solo lectura en emergencias, ya que el endpoint lo obtiene del usuario autenticado, y se corrigió el mock asíncrono de Channels en la prueba de monitoreo.
- Se configuró Nginx para propagar el `Host` original; sin esta directiva enviaba nombres internos con guion bajo y Django rechazaba las peticiones del Gateway con HTTP 400 (`DisallowedHost`).
- Se ejecutaron las 13 suites dentro de Docker: 51 pruebas superadas. También se verificaron los 17 contenedores activos, los 12 servicios de aplicación saludables, las 11 bases PostgreSQL, el BFF (HTTP 200), la redirección HTTP→HTTPS, el Gateway (HTTP 401 esperado sin JWT) y RabbitMQ/exchange `samr.events` (HTTP 200).
- No se modificaron modelos, flujos de negocio ni contratos de la arquitectura.

## 2026-07-20 — Infraestructura compartida del backend MVP (`logic/core-services`)

- Se normalizó el envelope v1.0 del publicador RabbitMQ, incluyendo serialización segura de UUID, Decimal y fechas, mensajes persistentes y confirmación de publicación.
- Se corrigió el consumidor compartido para invocar el contrato documentado `callback(event_type, payload)` y validar los campos obligatorios del envelope.
- Se implementó el límite declarativo de tres entregas mediante colas quorum de RabbitMQ 3.13 y un DLQ aislado por servicio; se corrigieron además los bindings para que reflejen el catálogo de `CORE_SERVICES.md`.
- Se añadió el middleware compartido de `X-Request-ID` y validación estricta de `Content-Type` definido por el rol Core Services.
- Las integraciones externas y reglas clínicas que no tienen contrato real se implementarán únicamente como adaptadores MVP reemplazables, por autorización expresa del usuario; nunca se presentarán como lógica clínica de producción.
- `auth-service` se alineó al esquema canónico: UUID, seis roles documentados, contador persistente de intentos y `locked_until`; el registro público fuerza el rol `patient` y valida contraseña alfanumérica de ocho caracteres como mínimo.
- Los JWT RS256 ahora incluyen emisor, `jti`, identificadores UUID serializados y tiempos documentados (15 minutos/7 días); el bloqueo se ejecuta transaccionalmente y su duración MVP se configura con `AUTH_LOCK_MINUTES`.
- `patient-service` se alineó a `patient_db`: UUID lógico, cédula cifrada con Fernet, tipo sanguíneo, listas clínicas, geolocalización decimal y tres consentimientos LOPDP; se eliminó el historial local porque el consolidado pertenece exclusivamente a M4.
- Se añadió `PATIENT_DATA_KEY` a la configuración backend y se documentó que la clave incluida es solo de desarrollo. El endpoint propio restringe el acceso al rol `patient` y el resumen M2M nunca expone la cédula.
- `solicitud-service` se alineó a sus tres tablas documentadas con UUID y eliminó campos/modelos ajenos al esquema. El chat usa un adaptador MVP que solo recupera FAQ administradas, informa confianza y deriva a revisión humana cuando no alcanza el umbral; no genera consejo clínico.
- La validación del Consorcio quedó detrás de `MVPConsortiumAdapter`, configurable para aceptación, rechazo o timeout. La tarea Celery conserva los estados `pendiente`, `validada`, `rechazada` y `pendiente_reintento` y publica únicamente los eventos del catálogo.
- Se añadió Redis al servicio de solicitud para el cache FAQ de 60 segundos y se documentaron `REDIS_URL`, `MVP_FAQ_CONFIDENCE_THRESHOLD`, `MVP_CONSORTIUM_OUTCOME` y `AUTH_LOCK_MINUTES`.
- `monitoring-service` se alineó a `vital_signs` y `monitoring_alerts` con UUID. La ingesta exige una Observation estructurada, token de dispositivo y registro previo recibido mediante `device.registered`; el registro habilitado se mantiene en Redis sin invadir la base M4.
- Se añadió cache Redis de las últimas 50 lecturas durante 120 segundos, alertas WebSocket y RBAC para personal clínico/administrativo. Los umbrales de anomalía son un adaptador técnico MVP configurable en `MVP_VITAL_THRESHOLDS`, expresamente no clínico.
- Se añadieron los procesos `consume_events` de M1: monitoring habilita dispositivos registrados por M4 y solicitud transforma `vitals.critical_detected` en una solicitud `iot_anomalia`, manteniendo la saga coreografiada sin llamadas directas entre bases de datos.
- `evaluacion-service` se alineó a las tres tablas de M2 con UUID: evaluaciones de riesgo, matching y cache de centros. Los eventos `center.validated/rejected` son la única fuente de su catálogo local.
- La evaluación MVP quedó aislada en reglas configurables y siempre declara `clinical_validation=false`; el matching determinista selecciona únicamente centros disponibles y exige identidad profesional, publicando `matching.fallido` cuando no existe candidato.
- El DTO de matching transporta `patient_id` sin persistirlo en M2 para que `recursos.asignados` pueda iniciar M3; así se mantiene el esquema documentado de `evaluacion_db` y la referencia sigue siendo lógica entre servicios.
- `teleconsult-service` se alineó al esquema UUID de M3, puede crear sesiones por endpoint o al consumir `recursos.asignados`, y publica `teleconsult.session_started`. El WebSocket autoriza participantes de una sala activa y rechaza todo mensaje que no sea `offer`, `answer` o `ice-candidate`.
- `emergency-service` se limitó a RF-14 con casos y guías UUID. Consume escalamiento/alertas críticas, publica creación y despacho, aplica RBAC y usa una guía MVP estática configurable que evita instrucciones clínicas inventadas.
- `cierre-caso-service` se alineó a `clinical_cases`, abre casos desde eventos de atención y exige notas, fuente de atención y SHA-256 reproducible antes de cerrar. Se añadió la lectura `mis-casos` requerida explícitamente por el contrato BFF de Core Services.
- `historial-interop-service` se redujo al expediente consolidado UUID, consume `caso.cerrado` de forma idempotente e invalida su cache FHIR. La exposición FHIR verifica `consent_sharing` por M2M con patient-service y cachea el Bundle 300 segundos; no simula envíos externos.
- Se añadió el cliente Redis requerido por el backend de cache de Django en historial-interop-service.
- `audit-service` se separó en evidencia `AuditLog` append-only y ciclo mutable `AuditReview`, consume el wildcard `#` y restringe lectura/revisión exclusivamente a `dpd_delegate`, sin alterar nunca el registro original.
- `admin-integracion-service` se alineó a centers/professionals/devices con UUID. Centros se validan mediante un adaptador M2M configurable y dispositivos publican `device.registered`; `serial_number` permanece solo en el DTO/evento porque el esquema aprobado no autoriza persistirlo.
- Se añadió Celery a admin-integracion-service para ejecutar la validación M2M de centros fuera del hilo HTTP, como exige Core Services.
- El BFF se limitó a propagar JWT al API Gateway y agrega en paralelo los cuatro contratos documentados (`patient`, `evaluacion`, `monitoring`, `atencion`); se eliminó TLS inseguro implícito y CORS wildcard.
- `notification-service` consume exclusivamente el catálogo de eventos notificables en un proceso separado y delega el envío a `MVPLogNotificationAdapter`; `MVP_NOTIFICATION_BACKEND=log` marca explícitamente que FCM aún es simulado.

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