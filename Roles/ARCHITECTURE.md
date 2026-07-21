# SAMR - Arquitectura de Sistema
## Rama `arch/system-design`

> Patrones arquitectónicos, topología, límites de microservicios por módulo, y estructura de despliegue. Para el detalle de base de datos ver `data/persistence-db`; para eventos/RabbitMQ ver `logic/core-services`; para seguridad ver `sec/security-hardening`.

---

# 1. Los 4 módulos de referencia y por qué se reorganizaron los servicios

Fuente de verdad: ESP-HS-SAMR v1.0.5 (Historias de Usuario) y el Diagrama de Clases (Apéndice A).

| Módulo | Caso de uso | RF que agrupa | Actores (Apéndice A) |
|---|---|---|---|
| **M1 - Módulo de Solicitud** | CU-001 | RF-01 a RF-07 | Usuario (Paciente/Familiar), LLM, RAG, Consorcio, DispositivoMonitoreo |
| **M2 - Módulo de Evaluación y Asignación** | CU-002 | RF-08 a RF-12 | LLM, RAG, ProfesionalSalud, CentroMedico |
| **M3 - Módulo de Atención** | CU-003 | RF-13 a RF-15 | ProfesionalSalud, Paciente, LLM, RAG, EnfermeroParamedico, Familiar |
| **M4 - Módulo de Integración e Interoperabilidad Clínica** | CU-004 | RF-16 a RF-20 | AdministradorSAMR, Usuario, EntidadExterna (IESS/MSP), Consorcio, DelegadoDPD |

**Principio rector:** un microservicio pertenece a un solo módulo de negocio (M1–M4). Ningún servicio mezcla responsabilidades de dos módulos distintos (excepto los explícitamente transversales: `auth-service`, `notification-service`, `bff-service`).

## Problemas de una versión anterior (ya corregidos aquí)

| Servicio (versión anterior) | Módulos que mezclaba | Corrección aplicada |
|---|---|---|
| `vity-ai-service` | M1 (chat/FAQ) + M2 (evaluación de riesgo) | Dividido: chat/FAQ → `solicitud-service` (M1); evaluación de riesgo → `evaluacion-service` (M2) |
| `emergency-service` | M1 (validación) + M2 (matching) + M3 (emergencias) | Validación → `solicitud-service` (M1); matching/asignación → `evaluacion-service` (M2); solo emergencias queda en `emergency-service` (M3) |
| `center-service` | M2 (lectura de catálogo) + M4 (registro/validación) | Lectura → `evaluacion-service` (M2, cache de solo lectura); registro/validación → `admin-integracion-service` (M4) |
| `monitoring-service` | M1 (ingesta IoT) + M4 (registro de dispositivos) | Ingesta/anomalías se queda en `monitoring-service` (M1); registro de dispositivos → `admin-integracion-service` (M4) |
| `followup-service` + `interop-service` | M3 + M4 separados sin necesidad | Cierre de caso → `cierre-caso-service` (M3); historial consolidado + FHIR → `historial-interop-service` (M4) |
| `bff-service` | - (mal ubicado en la topología) | Reposicionado: Frontend → BFF → API Gateway (antes vivía detrás del Gateway) |

---

# 2. Patrones Arquitectónicos Aplicados

| Patrón | Descripción | Aplicación en SAMR |
|---|---|---|
| **Database-per-Service** | Cada servicio posee su propio schema/base de datos; ningún JOIN entre schemas | 11 servicios con base de datos propia + 2 sin schema PostgreSQL propio (`notification-service` usa solo Redis, `bff-service` no persiste nada) |
| **API Gateway** | Punto único de entrada para todo el tráfico que llega a los microservicios | Nginx: routing por prefijo, rate limiting, WAF, TLS, verificación JWT previa (ver `sec/security-hardening`) |
| **Backend For Frontend (BFF), reubicado** | Capa de agregación **delante** del API Gateway, exclusiva del cliente web | `bff-service` recibe las peticiones del Frontend, agrega `patient + evaluacion + monitoring + atención` en una sola respuesta, y es quien llama al API Gateway - nunca al revés |
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
                                   │ HTTPS - el Frontend SOLO conoce la URL del BFF
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║  BFF-SERVICE - Backend For Frontend                                   ║
║  Agrega patient + evaluacion + monitoring + atencion para el          ║
║  dashboard en una sola respuesta. Sin base de datos propia.           ║
║  Es cliente del API Gateway, nunca al revés.                          ║
╚═════════════════════════════════╦════════════════════════════════════╝
                                   │ HTTPS :443 (TLS 1.3) interno
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║  NGINX - API GATEWAY                                                  ║
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
║  RABBITMQ 3.13 - Event Bus (exchange topic `samr.events`)             ║
║  + broker de Celery (una sola tecnología de mensajería)                ║
╚══════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════╗
║  REDIS 7.2 - Cache de lecturas + Channel Layer WebSocket (solamente)  ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Por qué el BFF va antes del Gateway y no detrás:** el BFF no es "un microservicio de negocio más" - no implementa ningún RF por sí mismo, solo agrega respuestas de otros servicios para reducir las llamadas paralelas que el dashboard tendría que hacer. Colocándolo delante, el contrato queda más limpio: *el Frontend solo habla con el BFF; el BFF solo habla con el Gateway; el Gateway es el único que conoce la topología interna de los 12 microservicios de negocio.*

---

# 4. Desglose de Microservicios (responsabilidades y endpoints, organizado por módulo)

> El esquema SQL de cada tabla vive en la rama `data/persistence-db`. Aquí solo se documenta responsabilidad, endpoints y eventos (el detalle de eventos está ampliado en `logic/core-services`).

## 4.0 Servicios Transversales

### `auth-service` :8001 - Autenticación e Identidad
**Responsabilidad única:** ciclo de vida de la identidad - registro, login, emisión/revocación de JWT (RS256), bloqueo por intentos fallidos, RBAC. Es el único servicio con la clave privada RSA.

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/auth/register/` | POST | Pública | RF-01 |
| `/api/auth/login/` | POST | Pública (rate-limited 5/min) | RF-01, RNF-01 |
| `/api/auth/token/refresh/` | POST | Refresh token | RNF-01 |
| `/api/auth/me/` | GET | JWT | RF-01 |

### `notification-service` :8012 - Notificaciones Multi-Canal
**Responsabilidad única:** despacho de notificaciones push (FCM). Servicio puramente reactivo, sin endpoints de negocio.

### `bff-service` - Backend For Frontend
**Responsabilidad única:** agregar `patient + evaluacion + monitoring + cierre-caso` en una sola respuesta para el dashboard. Reposicionado entre el Frontend y el Gateway (sección 3).

| Endpoint (directo al Frontend, no vía Nginx) | Método | Auth |
|---|---|---|
| `/dashboard/` | GET | JWT (propaga a servicios internos a través del Gateway) |

## 4.1 M1 - Módulo de Solicitud (CU-001 · RF-01 a RF-07)

### `patient-service` :8002 - Perfil Clínico del Paciente
**Responsabilidad única:** datos demográficos, alergias, condiciones crónicas, geolocalización, consentimientos LOPDP.

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/patients/me/` | GET/PATCH | JWT (paciente) | RF-01 |
| `/api/patients/{id}/summary/` | GET | X-Service-Token (M2M) | RF-08, RF-11 |

### `solicitud-service` :8003 - Bot Conversacional, Registro y Validación de Solicitud
**Responsabilidad única:** conversación con el paciente (RF-02, RF-07), registro de la solicitud médica (RF-03) y validación M2M con el Consorcio (RF-04).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/solicitud/chat/` | POST | JWT (paciente) | RF-02, RF-07 |
| `/api/solicitud/faq/` | GET/POST/PATCH | Admin JWT (POST/PATCH) | RF-07, RNF-12 |
| `/api/solicitud/` | POST | JWT (paciente) | RF-03 |
| `/api/solicitud/conversations/{id}/` | DELETE | JWT (dueño) | LOPDP - derecho al olvido |

**Flujo de validación M2M con el Consorcio (RF-04):**
```
1. Usuario/Dispositivo genera la solicitud → estado='pendiente', publica "solicitud.creada"
2. solicitud-service llama de forma asíncrona (Celery) al Consorcio para validar datos obligatorios
3. Si no hay respuesta en ≤ 5s o hay error → estado='pendiente_reintento' (RNF-07)
4. Si valida → estado='validada', publica "solicitud.validada" (consumido por evaluacion-service)
   Si rechaza → estado='rechazada'
```

### `monitoring-service` :8004 - IoT, Signos Vitales y Detección de Anomalías
**Responsabilidad única:** ingesta de datos IoT (RF-05), detección de anomalías (RF-06), WebSocket en tiempo real. No incluye registro administrativo de dispositivos (eso es `admin-integracion-service`, M4).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/monitoring/iot-events/` | POST | Device token | RF-05, RNF-08, RNF-09 |
| `/api/monitoring/alerts/` | GET | Medical/Admin JWT | RF-06 |
| `ws/monitoring/{patient_id}/` | WebSocket | JWT (query param) | RF-06, RNF-10 |

## 4.2 M2 - Módulo de Evaluación y Asignación (CU-002 · RF-08 a RF-12)

### `evaluacion-service` :8005 - Evaluación de Riesgo, Matching y Asignación de Recursos
**Responsabilidad única:** todo el ciclo de CU-002 en un solo servicio: evaluación de riesgo con IA (RF-08), recomendaciones RAG (RF-09), búsqueda de centros disponibles - solo lectura (RF-10), matching (RF-11), asignación de recursos + notificación (RF-12).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/evaluacion/riesgo/{solicitud_id}/` | GET | JWT | RF-08, RF-09 |
| `/api/evaluacion/centros-disponibles/` | GET | X-Service-Token | RF-10 |
| `/api/evaluacion/matching/{evaluacion_id}/` | POST | Medical/Admin JWT | RF-11, RF-12 |

## 4.3 M3 - Módulo de Atención (CU-003 · RF-13 a RF-15)

### `teleconsult-service` :8006 - Teleconsulta con Señalización WebRTC
**Responsabilidad única:** sesión de teleconsulta (RF-13) - creación de sala, señalización WebRTC, chat, notas médicas.

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/teleconsult/` | POST | Medical/Admin JWT | RF-13 |
| `ws/teleconsult/{room_token}/` | WebSocket (señalización SDP/ICE) | JWT (query param) | RF-13 |

### `emergency-service` :8007 - Gestión de Emergencias Médicas
**Responsabilidad única:** exclusivamente RF-14 - protocolo de emergencias, guía de primeros auxilios, despacho de ambulancia. Ya no hace matching (eso es M2) ni valida solicitudes (eso es M1).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/emergencies/` | POST/GET | JWT | RF-14 |
| `/api/emergencies/{id}/dispatch/` | POST | Admin/Medical JWT | RF-14 |

### `cierre-caso-service` :8008 - Actualización de Historial y Cierre del Caso
**Responsabilidad única:** actualización del historial clínico durante la atención y cierre operativo del caso (RF-15), verificación de integridad antes de cerrar (RNF-28).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/cierre-caso/{id}/close/` | POST | Medical JWT | RF-15, RNF-28 |
| `/api/cierre-caso/{id}/verify/` | GET | Medical/Admin JWT | RNF-28 |

## 4.4 M4 - Módulo de Integración e Interoperabilidad Clínica (CU-004 · RF-16 a RF-20)

### `historial-interop-service` :8009 - Historial Clínico Consolidado e Interoperabilidad FHIR
**Responsabilidad única:** expediente clínico consolidado por paciente (RF-16) y exposición en formato FHIR R4 a MSP/IESS/Consorcio (RF-17).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/historial/{patient_id}/` | GET | Medical/Patient JWT | RF-16 |
| `/api/history/fhir/{patient_id}/` | GET | Medical/Patient JWT + consentimiento | RF-17, RNF-32, RNF-34 |

### `audit-service` :8010 - Auditoría Inmutable y Auditoría DPD
**Responsabilidad única:** registro append-only de decisiones de IA (RF-18) y auditoría DPD (RF-20).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/audit/decisions/` | GET | JWT rol `dpd_delegate` | RF-20, RNF-38 |
| `/api/audit/decisions/{audit_log_id}/review/` | PATCH | JWT rol `dpd_delegate` | RF-20 |

### `admin-integracion-service` :8011 - Administración del Sistema (Centros y Dispositivos)
**Responsabilidad única:** RF-19 completo - registro y validación M2M con el Consorcio de nuevos centros médicos, y registro/vinculación de dispositivos IoT.

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
├── frontend/                       ← React SPA - solo conoce la URL del BFF
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
  # (resto de servicios: mismo patrón, sin JWT_PRIVATE_KEY_PATH - solo public.pem)

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
1. Ningún servicio importa código de otro servicio - aislamiento total.
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
