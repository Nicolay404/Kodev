# SAMR — Documento de Arquitectura Maestro y Definitivo
## Sistema de Atención Médica Remota · Arquitectura de Microservicios Orientada a Eventos (EDA)

> **Versión:** 4.0.0 — Realineada contra la Especificación de Historias de Usuario (ESP-HS-SAMR v1.0.5), el Diagrama de Clases (Apéndice A) y el archivo `requisitosfuncionaes_nofuncionales.xlsx` (20 RF · 38 RNF · 4 módulos).
> **Base de auditoría:** v3.0.0 de este mismo documento + los 3 artefactos anteriores.
> **Stack final (sin cambios de tecnología, solo de organización):** Django 5.0 · DRF 3.15 · Django Channels 4.1 · Celery 5.4 · **RabbitMQ 3.13** · Redis 7.2 · PostgreSQL 16 · React 18.3 · TypeScript 5.5 · Docker Compose.
> **Principio rector añadido en esta versión:** *Un microservicio pertenece a un solo módulo de negocio (M1–M4). Ningún servicio mezcla responsabilidades de dos módulos distintos.*

---

# 1. AUDITORÍA DE REALINEACIÓN (v3.0.0 → v4.0.0)

La versión 3.0.0 ya estaba bien auditada a nivel de **stack tecnológico** (RabbitMQ, JWT RS256, PostgreSQL, WebRTC), y esa parte **no cambia en esta versión**. Lo que se corrige aquí es la **identificación de los microservicios**: en v3.0.0 varios servicios mezclaban responsabilidades de más de uno de los 4 módulos definidos en la Especificación de Historias de Usuario (ESP-HS-SAMR v1.0.5) y en el Diagrama de Clases. Esta versión reorganiza los límites de servicio para que cada uno pertenezca a un solo módulo (M1–M4), y reposiciona el BFF entre el Frontend y el API Gateway.

## 1.1 Los 4 módulos de referencia (fuente de verdad: ESP-HS-SAMR v1.0.5 y el `.xlsx` de requisitos)

| Módulo | Caso de uso | RF que agrupa | Actores (según Apéndice A / clases del dominio) |
|---|---|---|---|
| **M1 — Módulo de Solicitud** | CU-001 | RF-01 a RF-07 | Usuario (Paciente/Familiar), LLM, RAG, Consorcio, DispositivoMonitoreo |
| **M2 — Módulo de Evaluación y Asignación** | CU-002 | RF-08 a RF-12 | LLM, RAG, ProfesionalSalud, CentroMedico |
| **M3 — Módulo de Atención** | CU-003 | RF-13 a RF-15 | ProfesionalSalud, Paciente, LLM, RAG, EnfermeroParamedico, Familiar |
| **M4 — Módulo de Integración e Interoperabilidad Clínica** | CU-004 | RF-16 a RF-20 | AdministradorSAMR, Usuario, EntidadExterna (IESS/MSP), Consorcio, DelegadoDPD |

## 1.2 Problemas detectados en v3.0.0 (por qué se reorganiza)

| Servicio en v3.0.0 | Módulos que mezclaba | Evidencia del conflicto |
|---|---|---|
| `vity-ai-service` | M1 (RF-02, RF-07) **y** M2 (RF-08, RF-09) | El chatbot/FAQ es M1 (Solicitud); la evaluación de riesgo con IA y las recomendaciones RAG son M2 (Evaluación), no la misma responsabilidad de negocio. |
| `emergency-service` | M1 (publicaba `solicitud.validada`) **+** M2 (matching RF-11, asignación RF-12) **+** M3 (emergencias RF-14) | La validación de la solicitud es responsabilidad de M1; el matching/asignación es M2; solo la gestión de emergencias (RF-14) es M3. Un mismo servicio no puede ser dueño de tres módulos. |
| `center-service` | M2 (búsqueda de centros, RF-10 — lectura) **y** M4 (registro/validación M2M de centros, RF-19 — escritura administrativa) | Consultar centros disponibles para un matching (M2) es una operación de lectura muy distinta, en dueño y en ciclo de vida, a dar de alta y validar un centro nuevo en el consorcio (M4, "Administración del Sistema"). |
| `monitoring-service` | M1 (ingesta IoT + anomalías, RF-05/RF-06) **y** M4 (registro de dispositivos por el Administrador, RF-19) | Ingerir datos biomédicos y detectar anomalías es parte del flujo de Solicitud (de hecho, dispara una nueva `SolicitudMedica`, ver CU-001 flujo alternativo); vincular un dispositivo a un paciente es una función administrativa de M4. |
| `followup-service` | M3 (cierre del caso, RF-15) **y** M4 (historial clínico consolidado, RF-16) | Actualizar el historial *durante* la atención y cerrar el caso es M3 (`CentroMedico.confirmarCierreCaso()` en el Diagrama de Clases); el expediente **consolidado e inter-institucional** (RF-16) es M4, junto con la interoperabilidad FHIR (RF-17) — de hecho ya vivían separados en `interop-service`. |
| `bff-service` | — (no mezclaba módulos, pero estaba mal ubicado en la topología) | Estaba descrito como un microservicio más *detrás* del API Gateway (Nginx), al mismo nivel que los servicios de negocio. Un BFF por definición se sitúa **entre el cliente y el Gateway**, no junto a los servicios que agrega. |

## 1.3 Qué cambia y qué NO cambia

**No cambia (ya estaba bien y sigue igual):**
- Stack tecnológico completo (Django, DRF, Celery, RabbitMQ, Redis, PostgreSQL, React).
- Patrón Database-per-Service, Saga coreografiada, Zero Trust con JWT RS256.
- `auth-service`, `teleconsult-service`, `notification-service` y `audit-service`: ya estaban correctamente acotados a un solo módulo (o eran, con justificación, transversales) y se mantienen prácticamente intactos.
- Los 20 RF y 38 RNF: no se modifica ninguno, solo se reasigna qué servicio implementa cada uno.

**Sí cambia (identificación de microservicios y topología):**
- De **12** a **13** microservicios, reorganizados para que cada uno pertenezca a un solo módulo M1–M4 (o sea explícitamente transversal, como `auth-service` y `notification-service`).
- `bff-service` se reposiciona: **Frontend → BFF → API Gateway (Nginx) → microservicios**, en vez de estar detrás del Gateway.
- Se elimina la mezcla de responsabilidades descrita en la tabla 1.2, moviendo cada responsabilidad al servicio de su módulo correspondiente.

---

# 2. ARQUITECTURA GENERAL Y TOPOLOGÍA

## 2.1 Patrones Arquitectónicos Aplicados

| Patrón | Descripción | Aplicación en SAMR |
|---|---|---|
| **Database-per-Service** | Cada servicio posee su propio schema/base de datos; ningún JOIN entre schemas | 11 servicios con base de datos propia + 2 servicios sin schema PostgreSQL propio (`notification-service` usa solo Redis, `bff-service` no persiste nada) |
| **API Gateway** | Punto único de entrada para todo el tráfico que llega a los microservicios | Nginx: routing por prefijo, rate limiting, WAF, TLS, verificación JWT previa |
| **Backend For Frontend (BFF), reubicado** | Capa de agregación **delante** del API Gateway, exclusiva del cliente web | `bff-service` recibe las peticiones del Frontend, agrega `patient + evaluacion + monitoring + atención` en una sola respuesta, y es quien llama al API Gateway (Nginx) para llegar a cada microservicio — nunca al revés |
| **Event-Driven / Coreografía** | Los servicios reaccionan a eventos publicados por otros, sin orquestador central | RabbitMQ (exchange topic `samr.events`); ningún servicio le "ordena" a otro qué hacer |
| **Saga Coreografiada** | Transacción distribuida sin coordinador central, con compensación hacia adelante | `solicitud.creada (M1) → riesgo.evaluado (M2) → recursos.asignados (M2) → atencion.iniciada (M3) → caso.cerrado (M3) → historial.consolidado (M4)` |
| **Un servicio, un módulo** *(nuevo en v4.0)* | Ningún microservicio implementa RF de dos módulos distintos | Ver tabla de la sección 1.2 y el desglose completo en la sección 4 |
| **Polyglot Persistence (mínimo necesario)** | Un motor por tipo de dato, sin motores redundantes | PostgreSQL (relacional + JSONB) para todo dato persistente; Redis solo para cache/canal WebSocket; RabbitMQ solo para mensajería |
| **Zero Trust interno** | Ningún servicio confía en otro por estar en la misma red | JWT RS256 (verificación local sin llamar a `auth-service`) + `X-Service-Token` en llamadas M2M |

## 2.2 Stack Tecnológico Global

*(Sin cambios respecto a v3.0.0 — se mantiene íntegro por ya estar correctamente auditado contra los RNF)*

### Backend — común a los 12 microservicios de negocio

| Tecnología | Versión | Uso |
|---|---|---|
| Django | 5.0.9 | Framework base (ORM, admin, middleware) |
| Django REST Framework | 3.15.2 | Serializers, ViewSets, permisos |
| djangorestframework-simplejwt | 5.3.1 | Validación JWT **RS256** |
| Daphne | 4.1.2 | Servidor ASGI (HTTP + WebSocket en un mismo proceso) |
| Django Channels | 4.1.0 | WebSocket — solo `monitoring-service` y `teleconsult-service` |
| channels-redis | 4.2.0 | Channel Layer sobre Redis |
| Celery | 5.4.0 | Workers asíncronos — broker: **RabbitMQ** |
| pika | 1.3.2 | Cliente RabbitMQ (publisher/consumer de eventos de dominio) |
| httpx | 0.27.0 | Cliente HTTP async (llamadas M2M, LLM, FHIR) |
| cryptography | 43.0.0 | Cifrado Fernet (AES-128) para campos PII: cédula |
| python-decouple | 3.8 | Variables de entorno desde `.env` |
| drf-spectacular | 0.27.2 | Documentación OpenAPI 3.0 automática |
| psycopg2-binary | 2.9.9 | Driver PostgreSQL |
| gunicorn | 22.0.0 | Lanza Daphne en producción |
| fhir.resources | 7.1.0 | Serialización HL7 FHIR R4 (solo `historial-interop-service`) |
| firebase-admin | 6.5.0 | Únicamente FCM (push) — solo `notification-service` |

### Frontend — un solo cliente React para todo el sistema

| Tecnología | Versión | Uso |
|---|---|---|
| React | 18.3.1 | Framework UI (componentes funcionales + hooks) |
| TypeScript | 5.5.3 | Tipado estático |
| Vite | 5.3.4 | Build tool y dev server |
| Zustand | 4.5.4 | Estado global por dominio (authStore, solicitudStore, monitoringStore, atencionStore) |
| Axios | 1.7.2 | Cliente HTTP con interceptores JWT |
| React Router DOM | 6.26.0 | Routing SPA con rutas protegidas por rol |
| @tanstack/react-query | 5.51.1 | Cache de datos del servidor, refetch automático |
| Radix UI | (paquetes individuales, última estable) | Componentes accesibles headless |
| Tailwind CSS | 3.4.7 | Sistema de diseño utilitario |
| React Hook Form | 7.52.1 | Formularios con validación |
| Zod | 3.23.8 | Validación de esquemas compartida con el backend |
| Recharts | 2.12.7 | Gráficas de signos vitales |
| react-hot-toast | 2.4.1 | Notificaciones toast |
| Framer Motion | 11.3.8 | Animaciones (estados de urgencia, bot) |
| i18next | 23.12.2 | Internacionalización ES/EN |

### Base de Datos e Infraestructura — el mínimo necesario

| Tecnología | Versión | Uso | RF/RNF que lo exige |
|---|---|---|---|
| PostgreSQL | 16 | Todo dato persistente (relacional + JSONB para esquema dinámico) | RNF-08, RNF-14, RNF-30, RNF-35, RNF-37 |
| Redis | 7.2 | Cache de lecturas frecuentes + Channel Layer de WebSocket **exclusivamente** | RNF-03, RNF-17a, RNF-20, RNF-36 |
| RabbitMQ | 3.13 | Event Bus de dominio + broker de Celery (una sola tecnología de mensajería) | RNF-07, RNF-10, RNF-18, RNF-21, RNF-27 |
| Nginx | 1.26.x (estable) | API Gateway: routing, TLS, rate limiting, WAF | RNF-06, RNF-25 |
| Docker + Docker Compose | Engine 27 / Compose v2 | Contenedor y orquestación local por servicio | Database-per-Service |
| Firebase Cloud Messaging | SDK 6.5.0 | Push notifications móviles | RNF-22, RNF-27 |
| coturn (TURN) + STUN público | coturn 4.6.2 | Conectividad WebRTC en redes restrictivas | RF-13 |

## 2.3 Topología de Red (BFF reubicado)

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

**Por qué el BFF va antes del Gateway y no detrás:** el BFF no es "un microservicio de negocio más" — no implementa ningún RF por sí mismo, solo agrega respuestas de otros servicios para reducir las llamadas paralelas que el dashboard tendría que hacer. Si se coloca detrás de Nginx (como en v3.0.0), el Frontend necesita conocer que existe un `bff-service` entre varios, y Nginx tendría que exponer una ruta especial solo para él sin razón. Colocándolo **delante**, el contrato queda más limpio: *el Frontend solo habla con el BFF; el BFF solo habla con el Gateway; el Gateway es el único que conoce la topología interna de los 12 microservicios de negocio.* Esto también evita que el BFF necesite pasar por el WAF/rate-limiting de Nginx para sus propias llamadas agregadas (son llamadas internas ya autenticadas con el JWT que el BFF propaga), mientras que todo el tráfico que sí debe pasar por Nginx (apps móviles, dispositivos IoT, el propio BFF) lo sigue haciendo de forma uniforme.

---

# 3. ESTRATEGIA DE COMUNICACIÓN — DETALLE TÉCNICO

## 3.1 Canal Síncrono — BFF y Clientes → Nginx → Microservicio

```nginx
# nginx/samr.conf
upstream auth_service               { server auth-service:8001; }
upstream patient_service            { server patient-service:8002; }
upstream solicitud_service          { server solicitud-service:8003; }
upstream monitoring_service         { server monitoring-service:8004; }
upstream evaluacion_service         { server evaluacion-service:8005; }
upstream teleconsult_service        { server teleconsult-service:8006; }
upstream emergency_service          { server emergency-service:8007; }
upstream cierre_caso_service        { server cierre-caso-service:8008; }
upstream historial_interop_service  { server historial-interop-service:8009; }
upstream audit_service              { server audit-service:8010; }
upstream admin_integracion_service  { server admin-integracion-service:8011; }
upstream notification_service       { server notification-service:8012; }

server {
    listen 443 ssl;
    ssl_protocols TLSv1.3;
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    # WAF básico — bloquea patrones de inyección antes de llegar a Django
    if ($request_uri ~* "(union|select|insert|drop|delete|--|;|<script)") { return 403; }

    limit_req_zone $binary_remote_addr zone=auth_zone:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api_zone:10m rate=30r/m;
    limit_req_zone $binary_remote_addr zone=iot_zone:10m rate=100r/m;

    # M1 — Solicitud
    location /api/auth/          { limit_req zone=auth_zone burst=3; proxy_pass http://auth_service; }
    location /api/patients/      { limit_req zone=api_zone;  proxy_pass http://patient_service; }
    location /api/solicitud/     { limit_req zone=api_zone;  proxy_pass http://solicitud_service; }
    location /api/monitoring/iot-events { limit_req zone=iot_zone; proxy_pass http://monitoring_service; }
    location /api/monitoring/    { limit_req zone=api_zone;  proxy_pass http://monitoring_service; }

    # M2 — Evaluación y Asignación
    location /api/evaluacion/    { limit_req zone=api_zone;  proxy_pass http://evaluacion_service; }

    # M3 — Atención
    location /api/teleconsult/   { limit_req zone=api_zone;  proxy_pass http://teleconsult_service; }
    location /api/emergencies/   { limit_req zone=api_zone;  proxy_pass http://emergency_service; }
    location /api/cierre-caso/   { limit_req zone=api_zone;  proxy_pass http://cierre_caso_service; }

    # M4 — Integración e Interoperabilidad Clínica
    location /api/historial/     { limit_req zone=api_zone;  proxy_pass http://historial_interop_service; }
    location /api/history/fhir/  { limit_req zone=api_zone;  proxy_pass http://historial_interop_service; }
    location /api/audit/         { limit_req zone=api_zone;  proxy_pass http://audit_service; }
    location /api/admin/         { limit_req zone=api_zone;  proxy_pass http://admin_integracion_service; }

    location /ws/monitoring/  { proxy_pass http://monitoring_service;  proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_read_timeout 86400s; }
    location /ws/teleconsult/ { proxy_pass http://teleconsult_service; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_read_timeout 86400s; }
}
```

```nginx
# nginx/bff.conf — el BFF vive delante de Nginx; este bloque es el propio
# API Gateway aceptando al BFF como cualquier otro cliente autenticado.
# location /api/bff/ NO existe en v4.0: el BFF ya no es una ruta más
# detrás del Gateway, es quien inicia las llamadas hacia las rutas de
# arriba (/api/patients/, /api/evaluacion/, /api/monitoring/, etc.)
```

## 3.2 Canal Asíncrono — RabbitMQ (Event Bus de Dominio)

*(El mecanismo de publicación/consumo — exchange topic, DLX, reintentos — no cambia respecto a v3.0.0; solo se actualiza qué servicio publica/consume cada evento, según la nueva identificación de microservicios.)*

```python
# shared/events/publisher.py — idéntico en todos los servicios
import pika, json, uuid
from datetime import datetime, timezone
from django.conf import settings

def publicar_evento(routing_key: str, payload: dict):
    conn = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = conn.channel()
    channel.exchange_declare(exchange="samr.events", exchange_type="topic", durable=True)

    mensaje = {
        "event_id": str(uuid.uuid4()),
        "event_type": routing_key,
        "service_origin": settings.SERVICE_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "payload": payload,
    }
    channel.basic_publish(
        exchange="samr.events",
        routing_key=routing_key,
        body=json.dumps(mensaje),
        properties=pika.BasicProperties(delivery_mode=2),  # persistente en disco
    )
    conn.close()

# Ejemplo de uso en solicitud-service (M1)
publicar_evento("solicitud.creada", {"solicitud_id": str(id), "patient_id": str(pid), "sintomas": [...]})
```

```python
# shared/events/consumer.py — patrón idéntico en todos los servicios
import pika, json
from django.conf import settings

def iniciar_consumidor(queue_name: str, routing_keys: list[str], callback):
    conn = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = conn.channel()
    channel.exchange_declare(exchange="samr.events", exchange_type="topic", durable=True)

    # Dead Letter Exchange: si un mensaje falla 3 veces, va a samr.events.dlx sin bloquear la cola principal
    channel.exchange_declare(exchange="samr.events.dlx", exchange_type="topic", durable=True)
    channel.queue_declare(queue=f"{queue_name}.dlq", durable=True)
    channel.queue_bind(queue=f"{queue_name}.dlq", exchange="samr.events.dlx", routing_key="#")

    channel.queue_declare(queue=queue_name, durable=True, arguments={
        "x-dead-letter-exchange": "samr.events.dlx",
        "x-max-retries": 3,
    })
    for rk in routing_keys:
        channel.queue_bind(queue=queue_name, exchange="samr.events", routing_key=rk)

    def on_message(ch, method, properties, body):
        try:
            evento = json.loads(body)
            callback(evento["event_type"], evento["payload"])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error procesando evento: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # → DLX tras agotar reintentos

    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    channel.start_consuming()
```

### Catálogo de Eventos Principales (reorganizado por módulo dueño)

| Routing key | Publicado por | Consumido por | Módulo | RF/RNF |
|---|---|---|---|---|
| `solicitud.creada` | `solicitud-service` | `evaluacion-service`, `audit-service` | M1 → M2 | RF-03 |
| `solicitud.validada` | `solicitud-service` (tras validación M2M con Consorcio) | `evaluacion-service` | M1 | RF-04 |
| `vitals.critical_detected` | `monitoring-service` | `solicitud-service` (crea solicitud automática), `notification-service`, `audit-service` | M1 | RF-06, RNF-10 |
| `device.registered` | `admin-integracion-service` | `monitoring-service` (habilita ingesta de ese device_id), `audit-service` | M4 → M1 | RF-19 |
| `riesgo.evaluado` | `evaluacion-service` | `evaluacion-service` (continúa su propio flujo de matching) | M2 | RF-08 |
| `vity.escalation_requested` | `evaluacion-service` | `emergency-service`, `notification-service`, `audit-service` | M2 → M3 | RF-08 |
| `recursos.asignados` | `evaluacion-service` | `teleconsult-service`, `notification-service` | M2 → M3 | RF-11, RF-12 |
| `matching.fallido` | `evaluacion-service` | `evaluacion-service` (reintento con siguiente candidato) | M2 | RNF-19 |
| `center.registration_requested` | `admin-integracion-service` | validador M2M interno (ver 4.11) | M4 | RF-19 |
| `center.validated` / `center.rejected` | Validador M2M (`admin-integracion-service`) | `evaluacion-service` (actualiza catálogo de lectura), `notification-service` | M4 → M2 | RF-19 |
| `emergency.created` | `emergency-service` | `notification-service`, `audit-service` | M3 | RF-14 |
| `emergency.dispatched` | `emergency-service` | `notification-service`, `audit-service`, `cierre-caso-service` | M3 | RF-14 |
| `teleconsult.session_started` | `teleconsult-service` | `notification-service` | M3 | RF-13 |
| `teleconsult.closed` | `teleconsult-service` | `cierre-caso-service` | M3 | RF-13 |
| `caso.cerrado` | `cierre-caso-service` | `historial-interop-service`, `audit-service` | M3 → M4 | RF-15, RF-16 |
| `ai.decision_logged` | `solicitud-service`, `evaluacion-service` | `audit-service` | M1/M2 → M4 | RF-18, RNF-35 |
| `auth.login_success` / `auth.account_locked` | `auth-service` | `audit-service` | Transversal | RNF-01 |

## 3.3 Canal Tiempo Real — WebSocket (Django Channels + Redis)

*(Sin cambios de tecnología respecto a v3.0.0 — solo se confirma que ambos servicios con WebSocket quedan cada uno en un solo módulo: `monitoring-service` es M1, `teleconsult-service` es M3.)*

```python
# config/asgi.py — monitoring-service (M1) y teleconsult-service (M3)
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddlewareRS256(
        URLRouter([
            path("ws/monitoring/<str:patient_id>/", MonitoringConsumer.as_asgi()),
            path("ws/teleconsult/<str:room_token>/", TeleconsultSignalingConsumer.as_asgi()),
        ])
    ),
})
```

```python
# settings/base.py
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [config("REDIS_URL")], "capacity": 1500, "expiry": 10},
    }
}
```

**Señalización WebRTC (teleconsulta, RF-13):** el WebSocket de `teleconsult-service` transporta únicamente mensajes de señalización (`offer`, `answer`, `ice-candidate`), nunca el video/audio en sí:

```python
# teleconsult-service/consumers/teleconsult.py
class TeleconsultSignalingConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Reenvía la señal WebRTC (offer/answer/ice-candidate) al otro participante de la sala
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "signal.message", "signal": data, "sender": self.scope["user"].id},
        )
```
Configuración del cliente (frontend): `RTCPeerConnection` con `iceServers: [{urls: "stun:stun.l.google.com:19302"}, {urls: "turn:turn.samr.local:3478", username, credential}]`. El TURN (`coturn`) solo se usa cuando la conexión directa P2P falla (redes con NAT simétrico o firewalls corporativos).

## 3.4 Canal Interno M2M — Llamadas HTTP entre Servicios (incluye el BFF)

```python
# Servicio receptor
class IsInternalService(BasePermission):
    def has_permission(self, request, view):
        return request.headers.get("X-Service-Token") == settings.INTERNAL_SERVICE_TOKEN

# BFF llamando al API Gateway (nunca a un microservicio directo — respeta la topología de 2.3)
headers = {"Authorization": f"Bearer {jwt_del_usuario}"}
async with httpx.AsyncClient(base_url="https://nginx-gateway") as client:
    patient, evaluacion, monitoring, atencion = await asyncio.gather(
        client.get("/api/patients/me/", headers=headers),
        client.get("/api/evaluacion/mis-casos/", headers=headers),
        client.get("/api/monitoring/alerts/", headers=headers),
        client.get("/api/cierre-caso/mis-casos/", headers=headers),
    )

# Llamada M2M puntual entre microservicios de negocio (ej. evaluacion-service → admin-integracion-service)
headers = {"X-Service-Token": settings.INTERNAL_SERVICE_TOKEN}
response = httpx.get("http://admin-integracion-service:8011/api/admin/centers/available/", headers=headers, timeout=5.0)
```
El token interno es distinto del JWT de usuario — identifica al *servicio* llamador, no a una persona. Rotación recomendada: cada 90 días, vía variable de entorno (sin cambios de código). El BFF es la única pieza que usa el JWT del usuario (propagándolo) en vez del `X-Service-Token`, porque actúa en nombre del usuario, no como un servicio interno más.

---

# 4. DESGLOSE DE MICROSERVICIOS (organizado por módulo)

## 4.0 Servicios Transversales (no pertenecen a un solo módulo)

### 4.0.1 `auth-service` :8001 — Autenticación e Identidad

**Responsabilidad única:** ciclo de vida de la identidad — registro, login, emisión/revocación de JWT (RS256), bloqueo por intentos fallidos, RBAC. Es el único servicio con la clave privada RSA. Aunque RF-01 está catalogado bajo M1 en la matriz de requisitos, la identidad se consulta (verificación de JWT) desde los 12 microservicios de negocio y el BFF, por lo que se documenta aparte como transversal.

**Base de datos:** PostgreSQL, schema `auth_db`.
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

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/auth/register/` | POST | Pública | RF-01 |
| `/api/auth/login/` | POST | Pública (rate-limited 5/min) | RF-01, RNF-01 |
| `/api/auth/token/refresh/` | POST | Refresh token | RNF-01 |
| `/api/auth/me/` | GET | JWT | RF-01 |

**Eventos que publica:** `auth.login_success`, `auth.account_locked`
**Eventos que consume:** ninguno (es la fuente de identidad, no reacciona a otros dominios)

### 4.0.2 `notification-service` :8012 — Notificaciones Multi-Canal

**Responsabilidad única:** despacho de notificaciones push (FCM). Servicio puramente reactivo — no expone endpoints de negocio, solo un health check. Es transversal porque recibe eventos de los 4 módulos por igual.

**Base de datos:** Redis únicamente — preferencias de canal + cola de reintentos con backoff exponencial (TTL 24h).

**Eventos que consume:** `vity.escalation_requested` (M2), `emergency.created`, `emergency.dispatched` (M3), `recursos.asignados` (M2), `center.validated`, `center.rejected` (M4)
**Eventos que publica:** ninguno

### 4.0.3 `bff-service` — Backend For Frontend (reposicionado, sin puerto interno de negocio)

**Responsabilidad única:** agregar `patient + evaluacion + monitoring + cierre-caso` en una sola respuesta para el dashboard del Frontend. **Ya no vive detrás del API Gateway como los demás**: se ubica entre el Frontend y Nginx (ver topología 2.3), y es él quien llama al Gateway, nunca al revés.

**Base de datos:** ninguna propia.

| Endpoint (expuesto directo al Frontend, no vía Nginx) | Método | Auth |
|---|---|---|
| `/dashboard/` | GET | JWT (propaga a servicios internos a través del Gateway) |

**Eventos:** ninguno — solo llamadas HTTP en paralelo hacia el API Gateway (`httpx.AsyncClient` + `asyncio.gather`).

## 4.1 M1 — Módulo de Solicitud (CU-001 · RF-01 a RF-07)

### 4.1.1 `patient-service` :8002 — Perfil Clínico del Paciente

**Responsabilidad única:** datos demográficos, alergias, condiciones crónicas, geolocalización, consentimientos LOPDP. Fuente de verdad del perfil (soporta RF-01 junto con `auth-service`).

**Base de datos:** PostgreSQL, schema `patient_db`.
```sql
CREATE TABLE patients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,           -- referencia lógica a auth_user.id (sin FK cross-schema)
    cedula_encrypted    BYTEA NOT NULL,           -- Fernet AES-128
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

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/patients/me/` | GET/PATCH | JWT (paciente) | RF-01 |
| `/api/patients/{id}/summary/` | GET | X-Service-Token (M2M) | RF-08, RF-11 |

**Eventos que publica:** `patient.profile_updated`
**Eventos que consume:** ninguno

### 4.1.2 `solicitud-service` :8003 — Bot Conversacional, Registro y Validación de Solicitud

**Responsabilidad única:** conversación con el paciente (RF-02, RF-07 — antes en `vity-ai-service`), registro de la solicitud médica (RF-03) y su **validación M2M con el Consorcio** (RF-04 — antes vivía, fuera de lugar, en `emergency-service`).

**Base de datos:** PostgreSQL, schema `solicitud_db`.
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
Redis: `vity_cache:{hash_del_mensaje}` (TTL 60s) — cache de respuestas frecuentes de FAQ (RNF-12).

**Flujo de validación M2M con el Consorcio (RF-04):**
```
1. Usuario/Dispositivo genera la solicitud → estado='pendiente', publica "solicitud.creada"
2. solicitud-service llama de forma asíncrona (Celery) al Consorcio para validar datos obligatorios
3. Si no hay respuesta en ≤ 5s o hay error → estado='pendiente_reintento' (RNF-07)
4. Si valida → estado='validada', publica "solicitud.validada" (consumido por evaluacion-service)
   Si rechaza → estado='rechazada'
```

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/solicitud/chat/` | POST | JWT (paciente) | RF-02, RF-07 |
| `/api/solicitud/faq/` | GET/POST/PATCH | Admin JWT (POST/PATCH) | RF-07, RNF-12 |
| `/api/solicitud/` | POST | JWT (paciente) | RF-03 |
| `/api/solicitud/conversations/{id}/` | DELETE | JWT (dueño) | LOPDP — derecho al olvido |

**Eventos que publica:** `solicitud.creada`, `solicitud.validada`, `ai.decision_logged`
**Eventos que consume:** `vitals.critical_detected` (crea una solicitud automática cuando el módulo de monitoreo detecta una anomalía)

### 4.1.3 `monitoring-service` :8004 — IoT, Signos Vitales y Detección de Anomalías

**Responsabilidad única:** ingesta de datos IoT (RF-05), detección de anomalías (RF-06) y transmisión en tiempo real vía WebSocket. **Ya no incluye el registro administrativo de dispositivos** (eso se movió a `admin-integracion-service`, M4, porque es una función de "Administración del Sistema", RF-19, no de recepción de datos clínicos).

**Base de datos:** PostgreSQL, schema `monitoring_db` + Redis (`vitals:{patient_id}`, TTL 120s, últimas 50 lecturas).
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

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/monitoring/iot-events/` | POST | Device token (X-Service-Token específico) | RF-05, RNF-08, RNF-09 |
| `/api/monitoring/alerts/` | GET | Medical/Admin JWT | RF-06 |
| `ws/monitoring/{patient_id}/` | WebSocket | JWT (query param) | RF-06, RNF-10 |

**Eventos que publica:** `vitals.critical_detected`
**Eventos que consume:** `device.registered` (habilita la ingesta de lecturas de ese `device_id`; sin este evento previo, `/api/monitoring/iot-events/` rechaza el dato)

## 4.2 M2 — Módulo de Evaluación y Asignación (CU-002 · RF-08 a RF-12)

### 4.2.1 `evaluacion-service` :8005 — Evaluación de Riesgo, Matching y Asignación de Recursos

**Responsabilidad única:** todo el ciclo de CU-002 en un solo servicio, porque son pasos secuenciales del mismo flujo de negocio y del mismo actor principal (LLM + Profesional/Evaluador clínico): evaluación de riesgo con IA (RF-08), recomendaciones con contexto RAG (RF-09), búsqueda de centros disponibles — **solo lectura** del catálogo que administra M4 (RF-10), matching paciente-profesional (RF-11) y asignación de recursos + notificación (RF-12). **Antes, RF-11/RF-12 vivían mal ubicados en `emergency-service`.**

**Base de datos:** PostgreSQL, schema `evaluacion_db` + réplica de lectura del catálogo de centros (actualizada por evento, ver 3.2).
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
CREATE TABLE centros_disponibles_cache (
    center_id   UUID PRIMARY KEY,          -- espejo de solo lectura de admin_db.centers
    nombre      VARCHAR(255),
    disponible  BOOLEAN DEFAULT TRUE
);
```

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/evaluacion/riesgo/{solicitud_id}/` | GET | JWT | RF-08, RF-09 |
| `/api/evaluacion/centros-disponibles/` | GET | X-Service-Token | RF-10 |
| `/api/evaluacion/matching/{evaluacion_id}/` | POST | Medical/Admin JWT | RF-11, RF-12 |

**Eventos que consume:** `solicitud.validada` (M1), `center.validated` / `center.rejected` (M4 — actualiza `centros_disponibles_cache`), `matching.fallido` (reintento con siguiente candidato)
**Eventos que publica:** `riesgo.evaluado`, `vity.escalation_requested`, `recursos.asignados`, `matching.fallido`, `ai.decision_logged`

## 4.3 M3 — Módulo de Atención (CU-003 · RF-13 a RF-15)

### 4.3.1 `teleconsult-service` :8006 — Teleconsulta con Señalización WebRTC

**Responsabilidad única:** sesión de teleconsulta (RF-13) — creación de sala, señalización WebRTC para video/audio, chat de texto, notas médicas y diagnóstico. Sin cambios respecto a v3.0.0 (ya estaba correctamente acotado a un solo módulo).

**Base de datos:** PostgreSQL, schema `teleconsult_db` + Redis (`room:{room_token}`, TTL 3600s: estado de sala).
```sql
CREATE TABLE teleconsults (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id     UUID NOT NULL, professional_id UUID NOT NULL,
    emergency_id   UUID NULL, room_token VARCHAR(64) UNIQUE NOT NULL,
    diagnosis      TEXT, ai_recommendation JSONB,
    status         VARCHAR(20) DEFAULT 'active', closed_at TIMESTAMPTZ NULL
);
```

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/teleconsult/` | POST | Medical/Admin JWT | RF-13 |
| `ws/teleconsult/{room_token}/` | WebSocket (señalización SDP/ICE) | JWT (query param) | RF-13 |

**Eventos que consume:** `recursos.asignados`
**Eventos que publica:** `teleconsult.session_started`, `teleconsult.closed`

### 4.3.2 `emergency-service` :8007 — Gestión de Emergencias Médicas

**Responsabilidad única:** **exclusivamente** RF-14 — activar el protocolo de emergencias, generar/entregar la guía de primeros auxilios, coordinar el despacho de ambulancia. **Ya no hace matching ni asignación de recursos** (eso quedó en `evaluacion-service`, M2) **ni valida solicitudes** (eso quedó en `solicitud-service`, M1).

**Base de datos:** PostgreSQL, schema `emergency_db`.
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

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/emergencies/` | POST/GET | JWT | RF-14 |
| `/api/emergencies/{id}/dispatch/` | POST | Admin/Medical JWT | RF-14 |

**Eventos que consume:** `vity.escalation_requested` (M2), `vitals.critical_detected` (M1)
**Eventos que publica:** `emergency.created`, `emergency.dispatched`, `ai.decision_logged`

### 4.3.3 `cierre-caso-service` :8008 — Actualización de Historial y Cierre del Caso

**Responsabilidad única:** actualización del historial clínico *durante* la atención y cierre operativo del caso (RF-15), verificación de integridad del expediente antes de cerrar (RNF-28). Se renombra desde `followup-service`: "seguimiento" ya no es un concepto vigente en la especificación de casos de uso (el CU-003 corregido no contempla una épica de "seguimiento y continuidad" separada), por lo que el nombre del servicio se alinea al RF-15 real: **cierre del caso**.

**Base de datos:** PostgreSQL, schema `cierre_db`.
```sql
CREATE TABLE clinical_cases (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id    UUID NOT NULL, teleconsult_id UUID NULL, emergency_id UUID NULL,
    clinical_notes TEXT, integrity_hash VARCHAR(64),  -- SHA-256
    status        VARCHAR(20) DEFAULT 'open', closed_at TIMESTAMPTZ NULL
);
```

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/cierre-caso/{id}/close/` | POST | Medical JWT | RF-15, RNF-28 |
| `/api/cierre-caso/{id}/verify/` | GET | Medical/Admin JWT | RNF-28 |

**Eventos que consume:** `teleconsult.closed`, `emergency.dispatched`
**Eventos que publica:** `caso.cerrado` (consumido por `historial-interop-service` en M4 para consolidar el expediente — este es el punto exacto donde M3 entrega la información a M4)

## 4.4 M4 — Módulo de Integración e Interoperabilidad Clínica (CU-004 · RF-16 a RF-20)

### 4.4.1 `historial-interop-service` :8009 — Historial Clínico Consolidado e Interoperabilidad FHIR

**Responsabilidad única:** mantener el expediente clínico **consolidado** por paciente (RF-16 — agregando eventos de M1/M2/M3) y exponerlo en formato FHIR R4 a MSP/IESS/Consorcio (RF-17). Se fusionan aquí dos responsabilidades que en v3.0.0 estaban separadas sin necesidad (`followup-service` guardaba el historial "local" y `interop-service` solo componía sin guardar nada): ambas son, en realidad, la misma responsabilidad de M4 vista desde dos ángulos (guardar el consolidado / exponerlo estandarizado).

**Base de datos:** PostgreSQL, schema `historial_db`.
```sql
CREATE TABLE expedientes_consolidados (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL,
    eventos         JSONB NOT NULL DEFAULT '[]',  -- solicitudes, teleconsultas, emergencias, decisiones IA
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_expediente_gin ON expedientes_consolidados USING GIN (eventos);
```
Redis: cache de la composición FHIR (TTL 300s).

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/historial/{patient_id}/` | GET | Medical/Patient JWT | RF-16 |
| `/api/history/fhir/{patient_id}/` | GET | Medical/Patient JWT + consentimiento verificado | RF-17, RNF-32, RNF-34 |

**Eventos que consume:** `caso.cerrado` (M3 — consolida el evento y, si aplica, invalida el cache FHIR)
**Eventos que publica:** ninguno

### 4.4.2 `audit-service` :8010 — Auditoría Inmutable y Auditoría DPD

**Responsabilidad única:** registro append-only de eventos de seguridad y decisiones de IA (RF-18), y la interfaz de Auditoría DPD (RF-20). Sin cambios respecto a v3.0.0 — ya estaba correctamente acotado a M4.

**Base de datos:** PostgreSQL, schema `audit_db`.
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

-- Tabla separada para el estado de revisión del DPD (AuditoriaTrazabilidad.estadoRevision
-- en el Apéndice A). Vive aparte de audit_log a propósito: revisarAuditoria() necesita
-- poder actualizar un estado, y audit_log es append-only por diseño (RNF-35, no repudio).
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

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/audit/decisions/` | GET | JWT rol `dpd_delegate` únicamente | RF-20, RNF-38 |
| `/api/audit/decisions/{audit_log_id}/review/` | PATCH | JWT rol `dpd_delegate` únicamente | RF-20 |

La operación `revisarAuditoria()` del Apéndice A (clase `DelegadoDPD`) se implementa como el `PATCH` de arriba: crea o actualiza la fila correspondiente en `audit_reviews`, nunca en `audit_log`.

**Eventos que consume:** *todos* los eventos del bus (`#` wildcard) — registra cada evento de dominio
**Eventos que publica:** ninguno

### 4.4.3 `admin-integracion-service` :8011 — Administración del Sistema (Centros y Dispositivos)

**Responsabilidad única:** el flujo de "Administración del Sistema" (RF-19) completo: registro y **validación M2M con el Consorcio** de nuevos centros médicos, y registro/vinculación de dispositivos IoT. Reúne, bajo un solo servicio de M4, lo que en v3.0.0 estaba repartido incorrectamente entre `center-service` (M2+M4 mezclados) y `monitoring-service` (M1+M4 mezclados).

**Base de datos:** PostgreSQL, schema `admin_db`.
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

**Flujo — Validación M2M automática con el Consorcio (RF-19):**
```
1. Admin: POST /api/admin/centers/register/  → status='pending_validation'
2. admin-integracion-service publica "center.registration_requested" {center_id, license_number, specialties, geo}
3. Validador M2M (worker Celery interno) verifica licencia, especialidades y cobertura geográfica
4. Si todo pasa → status='validated', publica "center.validated"
   Si falla algo → status='rejected', publica "center.rejected" {motivo}
5. notification-service notifica al admin el resultado
   evaluacion-service actualiza su cache de lectura (centros_disponibles_cache)
```

**Flujo — Registro de Dispositivos IoT (RF-19):**
```
POST /api/admin/devices/register/  {patient_id, device_type, serial_number}
   Restringido a rol system_admin
   → INSERT INTO devices (...)
   → publica "device.registered"
   Ninguna lectura de un device_id no registrado es aceptada por monitoring-service (M1)
```

| Endpoint | Método | Auth | RF/RNF |
|---|---|---|---|
| `/api/admin/centers/register/` | POST | Admin JWT (`system_admin`) | RF-19 |
| `/api/admin/centers/available/` | GET | X-Service-Token (leído por `evaluacion-service`) | RF-10 |
| `/api/admin/devices/register/` | POST | Admin JWT (`system_admin`) | RF-19 |

**Eventos que consume:** ninguno
**Eventos que publica:** `center.registration_requested`, `center.validated`, `center.rejected`, `device.registered`

---

# 5. ESPECIFICACIONES DETALLADAS POR ROL (Guía para Claude Code)

## 5.1 Arquitectura de Software

**Estructura de carpetas obligatoria:**
```
samr/
├── frontend/                       ← React SPA — solo conoce la URL del BFF
├── bff/
│   └── bff-service/                ← delante del Gateway (ver topología 2.3)
├── nginx/samr.conf                 ← API Gateway
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
│   ├── events/publisher.py        ← idéntico en los 12 servicios (copiar, no importar entre servicios)
│   └── events/consumer.py
├── event-schemas/                 ← 1 archivo JSON Schema por routing key del catálogo (sección 3.2)
├── scripts/
│   ├── init-db.sh                 ← crea los 11 schemas PostgreSQL
│   └── init-rabbitmq.sh           ← declara exchange, colas y DLX
├── docker-compose.yml
└── .env.example
```

**Estructura interna por cada servicio Django (sin cambios respecto a v3.0.0):**
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

**Orden de generación de código recomendado para Claude Code:**
1. `docker-compose.yml` + `nginx/samr.conf`
2. `scripts/init-db.sh` + `scripts/init-rabbitmq.sh`
3. `shared/events/{publisher,consumer}.py` (una sola vez, luego copiar a cada servicio)
4. `auth-service/` completo (genera par de claves RSA, base del sistema)
5. **M1:** `patient-service/`, `solicitud-service/`, `monitoring-service/`
6. **M2:** `evaluacion-service/`
7. **M3:** `teleconsult-service/`, `emergency-service/`, `cierre-caso-service/`
8. **M4:** `historial-interop-service/`, `audit-service/`, `admin-integracion-service/`
9. `notification-service/`
10. `frontend/` + `bff/bff-service/`

**Reglas absolutas para Claude Code (pegar en el prompt de generación):**
1. Ningún servicio importa código de otro servicio — aislamiento total.
2. Ningún microservicio implementa RF de más de un módulo (M1–M4) — ver sección 4 para la asignación exacta.
3. JWT: solo `auth-service` firma (RS256, clave privada); los demás solo verifican (clave pública).
4. Un schema PostgreSQL por servicio, sin Foreign Keys entre schemas.
5. Comunicación entre servicios: RabbitMQ para eventos de dominio; `X-Service-Token` para llamadas HTTP M2M puntuales.
6. El `bff-service` es el único que llama al API Gateway usando el JWT del usuario propagado; el Frontend nunca llama a Nginx directamente.
7. Docker multi-stage, usuario no-root, `HEALTHCHECK` incluido.
8. Celery: broker = RabbitMQ; `autodiscover_tasks(['tasks'])`.
9. Un test mínimo por endpoint (`APIClient` de DRF).
10. `README.md` por servicio con instalación y ejecución local.
11. Generar primero la estructura de carpetas completa antes de escribir código.

## 5.2 Base de Datos

- **UUID como clave primaria** en todas las tablas de negocio (`gen_random_uuid()`), excepto `audit_log` que usa `BIGSERIAL` (orden de inserción es parte de la evidencia de auditoría).
- **Convención de nombres de schema:** `{dominio}_db` en minúsculas (`auth_db`, `patient_db`, `solicitud_db`, `monitoring_db`, `evaluacion_db`, `teleconsult_db`, `emergency_db`, `cierre_db`, `historial_db`, `audit_db`, `admin_db`).
- **JSONB para esquema dinámico** (conversaciones Vity, expediente consolidado, payload de eventos en `audit_log`) — nunca una tabla EAV ni columnas nullable especulativas.
- **Inmutabilidad declarativa:** cualquier tabla de auditoría/trazabilidad debe tener su `REVOKE UPDATE, DELETE` documentado en `scripts/init-db.sh`, no solo confiado al código de la aplicación.
- **Índices obligatorios:** `patient_id` en toda tabla que lo contenga (consulta más frecuente del sistema); `GIN` sobre columnas `JSONB` consultadas por contenido.
- **Sin Foreign Keys entre schemas** — las referencias a `patient_id`/`user_id`/`device_id`/`center_id` de otro servicio son *lógicas* (UUID), nunca `REFERENCES` cruzado. La consistencia se garantiza por evento, no por constraint de base de datos.
- **Script de inicialización (`scripts/init-db.sh`):** crea los 11 schemas de negocio, ejecuta `python manage.py migrate` de cada servicio, y aplica los `REVOKE` de la tabla `audit_log`.

## 5.3 Backend

**Configuración compartida (`settings/base.py`, idéntica salvo el nombre de la app instalada):**
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ALGORITHM": "RS256",
    "VERIFYING_KEY": open(config("JWT_PUBLIC_KEY_PATH")).read(),
    # SIGNING_KEY solo se define en auth-service/settings/base.py
}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}
CELERY_BROKER_URL = config("RABBITMQ_URL")
CELERY_RESULT_BACKEND = "rpc://"
```

**Middleware compartido (`shared/middleware/security.py`):** `X-Request-ID` por petición (trazabilidad entre logs de distintos servicios), validación estricta de `Content-Type`.

**Tareas asíncronas (Celery):** todo cómputo que consulte otro servicio o tarde más de ~1 segundo va a un worker Celery, nunca en el hilo de la petición HTTP — aplica directamente a `evaluar_riesgo` y `ejecutar_matching` (evaluacion-service), `validar_solicitud_m2m` (solicitud-service), `validar_centro_m2m` (admin-integracion-service), envío de notificaciones (notification-service).

**Manejo de eventos:** cada servicio arranca su(s) consumidor(es) RabbitMQ en un proceso separado (`manage.py consume_events`), nunca en el mismo hilo que atiende HTTP.

## 5.4 Frontend

- **El Frontend solo conoce la URL del BFF** (`VITE_BFF_URL`) — ya no la del API Gateway directamente. El BFF es quien conoce la URL del Gateway, y el Gateway quien conoce la topología interna de los 12 microservicios. Esto profundiza el mismo principio que v3.0.0 ya aplicaba ("el frontend no conoce las URLs internas"), añadiendo una capa más de indirección correcta para el patrón BFF.
- **Gestión de estado:** Zustand por dominio (`authStore`, `solicitudStore`, `monitoringStore`, `evaluacionStore`, `atencionStore`) — sin Redux, evita boilerplate innecesario para dominios que no se comunican entre sí.
- **Peticiones HTTP:** Axios con interceptor que adjunta el JWT y reintenta una vez tras refrescar el token en un 401. Todas las peticiones van al BFF, no a Nginx.
- **Datos del servidor:** `@tanstack/react-query` con `stale-while-revalidate` — la pantalla muestra el último dato conocido mientras refresca en segundo plano.
- **Resiliencia:** `ErrorBoundary` por módulo (un fallo de `solicitud-service` no debe tumbar la pantalla de monitoreo), `SkeletonLoader` en toda carga remota, reconexión WebSocket con backoff exponencial (1s→2s→4s→8s→30s máx.), banner de estado offline tras 3 intentos fallidos.
- **WebRTC (teleconsulta):** `RTCPeerConnection` en el cliente, señalización vía el WebSocket ya definido en 3.3; sin librería adicional de video — WebRTC es nativo del navegador.

## 5.5 Seguridad

**Zero Trust interno:**
1. **Red:** todos los servicios en red Docker privada, sin puertos expuestos salvo Nginx `:443` y el `bff-service` (único punto de entrada del Frontend).
2. **JWT descentralizado (RS256):** cada servicio verifica el token con la clave pública, sin llamar a `auth-service` en cada petición y sin poder *emitir* tokens.
3. **RBAC explícito por vista**, no solo en el login: `permission_classes` específicas (`IsMedicalStaff`, `IsSystemAdmin`, `IsDPDDelegate`, `IsOwnerOrAdmin`) evaluadas en cada petición.
4. **Cifrado en reposo:** Fernet (AES-128 + HMAC-SHA256) para cédula (patient-service); clave `FIELD_ENCRYPTION_KEY` solo en variables de entorno, nunca en código ni en la base de datos.
5. **Cifrado en tránsito:** TLS 1.3 en Nginx y entre el Frontend y el BFF; tráfico interno Docker sin TLS (red privada, no expuesta).
6. **Rate limiting + WAF** en Nginx (sección 3.1) — primera línea de defensa contra fuerza bruta y SQLi, antes de que la petición llegue a Django. El `bff-service`, al ser el único cliente autenticado que llama al Gateway desde dentro de la red de confianza, no necesita repetir el WAF — Nginx lo sigue aplicando igual a su tráfico.
7. **Validación ORM:** Django ORM usa queries parametrizadas por defecto — sin concatenación de SQL en ningún servicio.
8. **Inmutabilidad de auditoría** a nivel de motor (`REVOKE UPDATE, DELETE`), no solo a nivel de aplicación.
9. **Consentimiento LOPDP:** `patient-service` mantiene `consent_data`, `consent_ai`, `consent_sharing` como campos explícitos; ningún servicio de IA procesa datos sin verificar `consent_ai=True`.
10. **Auditoría DPD restringida:** el endpoint de auditoría (`audit-service`) solo es accesible por el rol `dpd_delegate` — 403 inmediato para cualquier otro rol, sin exponer datos parciales.
11. **Token de servicio interno** (`X-Service-Token`) distinto del JWT de usuario para toda llamada M2M — rotación cada 90 días.

## 5.6 UX/UI

- **Accesibilidad WCAG 2.1 AA** como requisito funcional, no estético: contraste mínimo 4.5:1 (7:1 en alertas críticas), navegación completa por teclado, `aria-live="assertive"` en alertas de nivel crítico, áreas táctiles mínimas de 44×44px.
- **Jerarquía de urgencia con semiótica redundante** (color + ícono + tipografía), nunca solo color — accesible para usuarios con daltonismo: crítico (rojo, pulso 1Hz), alto (naranja), moderado (amarillo), leve (verde).
- **Comunicación de procesos asíncronos** (evaluación de riesgo IA, matching) mediante mensajes de progreso contextuales y Skeleton loaders — nunca un spinner genérico ni una barra de progreso falsa, para reducir la ansiedad percibida en momentos de urgencia médica.
- **Componentes:** Radix UI (headless, accesible por defecto) + Tailwind CSS para el sistema de diseño — evita reconstruir accesibilidad desde cero.

---

*Documento de Arquitectura Maestro SAMR v4.0 — realineado contra ESP-HS-SAMR v1.0.5 (4 módulos), el Diagrama de Clases (Apéndice A) y `requisitosfuncionaes_nofuncionales.xlsx` (20 RF · 38 RNF).*
*Stack final (sin cambios): Django 5.0 · DRF · Channels · Celery · RabbitMQ · Redis · PostgreSQL 16 · Nginx · React 18 · TypeScript · Docker.*
