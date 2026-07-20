# SAMR — Lógica de Negocio y Comunicación entre Servicios
## Rama `logic/core-services`

> Event Bus (RabbitMQ), catálogo de eventos de dominio, canal WebSocket en tiempo real, llamadas M2M y configuración de tareas asíncronas (Celery). Para responsabilidades de cada servicio ver `arch/system-design`; para los esquemas de datos que estos eventos leen/escriben ver `data/persistence-db`.

---

# 1. Canal Asíncrono — RabbitMQ (Event Bus de Dominio)

Un único **exchange topic** llamado `samr.events`. Cada servicio declara su propia **cola** ligada a los *routing keys* que le interesan — patrón estándar de mensajería, sin código de reintento manual: RabbitMQ reencola automáticamente si el consumidor no confirma.

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

**Por qué RabbitMQ y no Redis Streams:** ACK/NACK nativos, reintentos con Dead Letter Exchange configurado declarativamente (no en código), plugin de administración con UI web (`:15672`) para inspeccionar colas, y es la combinación históricamente más probada con Celery (que ya se usa para tareas asíncronas) — una sola tecnología de mensajería para eventos de dominio y tareas async, en vez de dos.

---

# 2. Catálogo de Eventos Principales (organizado por módulo dueño)

| Routing key | Publica | Consume | Módulo | RF/RNF |
|---|---|---|---|---|
| `solicitud.creada` | `solicitud-service` | `evaluacion-service`, `audit-service` | M1 → M2 | RF-03 |
| `solicitud.validada` | `solicitud-service` (tras validación M2M con Consorcio) | `evaluacion-service` | M1 | RF-04 |
| `vitals.critical_detected` | `monitoring-service` | `solicitud-service` (crea solicitud automática), `notification-service`, `audit-service` | M1 | RF-06, RNF-10 |
| `device.registered` | `admin-integracion-service` | `monitoring-service` (habilita ingesta de ese device_id), `audit-service` | M4 → M1 | RF-19 |
| `riesgo.evaluado` | `evaluacion-service` | `evaluacion-service` (continúa su propio flujo de matching) | M2 | RF-08 |
| `vity.escalation_requested` | `evaluacion-service` | `emergency-service`, `notification-service`, `audit-service` | M2 → M3 | RF-08 |
| `recursos.asignados` | `evaluacion-service` | `teleconsult-service`, `notification-service` | M2 → M3 | RF-11, RF-12 |
| `matching.fallido` | `evaluacion-service` | `evaluacion-service` (reintento con siguiente candidato) | M2 | RNF-19 |
| `center.registration_requested` | `admin-integracion-service` | validador M2M interno | M4 | RF-19 |
| `center.validated` / `center.rejected` | Validador M2M (`admin-integracion-service`) | `evaluacion-service` (actualiza catálogo de lectura), `notification-service` | M4 → M2 | RF-19 |
| `emergency.created` | `emergency-service` | `notification-service`, `audit-service` | M3 | RF-14 |
| `emergency.dispatched` | `emergency-service` | `notification-service`, `audit-service`, `cierre-caso-service` | M3 | RF-14 |
| `teleconsult.session_started` | `teleconsult-service` | `notification-service` | M3 | RF-13 |
| `teleconsult.closed` | `teleconsult-service` | `cierre-caso-service` | M3 | RF-13 |
| `caso.cerrado` | `cierre-caso-service` | `historial-interop-service`, `audit-service` | M3 → M4 | RF-15, RF-16 |
| `ai.decision_logged` | `solicitud-service`, `evaluacion-service` | `audit-service` | M1/M2 → M4 | RF-18, RNF-35 |
| `auth.login_success` / `auth.account_locked` | `auth-service` | `audit-service` | Transversal | RNF-01 |

`audit-service` consume además `#` (wildcard) — registra todos los eventos del bus, sin excepción.

**Flujo Saga crítico (coreografiado, sin orquestador):**
```
solicitud-service (M1: chat + registro) → solicitud.creada / solicitud.validada
  → evaluacion-service (M2: riesgo + matching) → recursos.asignados / vity.escalation_requested
  → teleconsult-service (M3) o emergency-service (M3, si es emergencia física)
  → teleconsult.closed / emergency.dispatched
  → cierre-caso-service (M3) → caso.cerrado
  → historial-interop-service (M4, consolida + invalida cache FHIR)
```

---

# 3. Canal Tiempo Real — WebSocket (Django Channels + Redis)

Ambos servicios con WebSocket quedan cada uno en un solo módulo: `monitoring-service` es M1, `teleconsult-service` es M3.

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
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "signal.message", "signal": data, "sender": self.scope["user"].id},
        )
```
Configuración del cliente (ver `ui/frontend-app` para el detalle React): `RTCPeerConnection` con `iceServers: [{urls: "stun:stun.l.google.com:19302"}, {urls: "turn:turn.samr.local:3478", username, credential}]`. El TURN (`coturn`) solo se usa cuando la conexión directa P2P falla.

---

# 4. Canal Interno M2M — Llamadas HTTP entre Servicios (incluye el BFF)

```python
# BFF llamando al API Gateway (nunca a un microservicio directo)
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
El token interno (`X-Service-Token`) identifica al *servicio* llamador, no a una persona — la validación de este token y el JWT del usuario se detallan en `sec/security-hardening`. El BFF es la única pieza que usa el JWT del usuario (propagándolo) en vez del `X-Service-Token`, porque actúa en nombre del usuario.

---

# 5. Backend — Configuración de Tareas Asíncronas

**Configuración Celery compartida (`settings/base.py`):**
```python
CELERY_BROKER_URL = config("RABBITMQ_URL")
CELERY_RESULT_BACKEND = "rpc://"
```

**Middleware compartido (`shared/middleware/security.py`):** `X-Request-ID` por petición (trazabilidad entre logs de distintos servicios), validación estricta de `Content-Type`.

**Tareas asíncronas (Celery):** todo cómputo que consulte otro servicio o tarde más de ~1 segundo va a un worker Celery, nunca en el hilo de la petición HTTP:
- `evaluar_riesgo` y `ejecutar_matching` — `evaluacion-service`
- `validar_solicitud_m2m` — `solicitud-service`
- `validar_centro_m2m` — `admin-integracion-service`
- envío de notificaciones — `notification-service`

**Manejo de eventos:** cada servicio arranca su(s) consumidor(es) RabbitMQ en un proceso separado (`manage.py consume_events`), nunca en el mismo hilo que atiende HTTP.

---
*Ver también: `arch/system-design` (topología y responsabilidades), `data/persistence-db` (qué tabla escribe/lee cada evento), `sec/security-hardening` (JWT, `X-Service-Token`, rate limiting en Nginx).*
