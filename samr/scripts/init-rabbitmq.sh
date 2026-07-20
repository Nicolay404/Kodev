#!/bin/bash
set -e

echo "Inicializando RabbitMQ..."

# Requiere rabbitmqadmin o curl. Usamos API HTTP mediante curl para máxima compatibilidad.
RABBITMQ_API="http://guest:guest@rabbitmq:15672/api"
VHOST="%2F" # Default vhost '/' url-encoded

# 1. Crear Exchanges
curl -s -u guest:guest -X PUT "$RABBITMQ_API/exchanges/$VHOST/samr.events" \
    -H "content-type:application/json" \
    -d '{"type":"topic","auto_delete":false,"durable":true,"internal":false}'

curl -s -u guest:guest -X PUT "$RABBITMQ_API/exchanges/$VHOST/samr.events.dlx" \
    -H "content-type:application/json" \
    -d '{"type":"topic","auto_delete":false,"durable":true,"internal":false}'

SERVICES=(
    "auth-service"
    "notification-service"
    "patient-service"
    "solicitud-service"
    "monitoring-service"
    "evaluacion-service"
    "teleconsult-service"
    "emergency-service"
    "cierre-caso-service"
    "historial-interop-service"
    "audit-service"
    "admin-integracion-service"
)

for svc in "${SERVICES[@]}"; do
    QUEUE_NAME="${svc}.queue"
    DLQ_NAME="${svc}.queue.dlq"
    
    # Crear Cola Principal (con DLX)
    curl -s -u guest:guest -X PUT "$RABBITMQ_API/queues/$VHOST/$QUEUE_NAME" \
        -H "content-type:application/json" \
        -d '{"auto_delete":false,"durable":true,"arguments":{"x-dead-letter-exchange":"samr.events.dlx"}}'
        
    # Crear DLQ
    curl -s -u guest:guest -X PUT "$RABBITMQ_API/queues/$VHOST/$DLQ_NAME" \
        -H "content-type:application/json" \
        -d '{"auto_delete":false,"durable":true,"arguments":{}}'
        
    # Bind DLQ a DLX con routing key del servicio
    curl -s -u guest:guest -X POST "$RABBITMQ_API/bindings/$VHOST/e/samr.events.dlx/q/$DLQ_NAME" \
        -H "content-type:application/json" \
        -d '{"routing_key":"#"}'
done

# Función helper para bindings
bind_queue() {
    local queue=$1
    local rk=$2
    curl -s -u guest:guest -X POST "$RABBITMQ_API/bindings/$VHOST/e/samr.events/q/$queue" \
        -H "content-type:application/json" \
        -d "{\"routing_key\":\"$rk\"}"
}

# Aplicar bindings específicos basados en CORE_SERVICES.md
bind_queue "solicitud-service.queue" "solicitud.creada"
bind_queue "evaluacion-service.queue" "solicitud.validada"
bind_queue "evaluacion-service.queue" "vitals.critical_detected"
bind_queue "teleconsult-service.queue" "recursos.asignados"
bind_queue "teleconsult-service.queue" "vity.escalation_requested"
bind_queue "emergency-service.queue" "vitals.critical_detected"
bind_queue "emergency-service.queue" "vity.escalation_requested"
bind_queue "cierre-caso-service.queue" "teleconsult.session_started"
bind_queue "cierre-caso-service.queue" "teleconsult.closed"
bind_queue "cierre-caso-service.queue" "emergency.dispatched"
bind_queue "historial-interop-service.queue" "caso.cerrado"
bind_queue "audit-service.queue" "#" # wildcard
bind_queue "notification-service.queue" "auth.account_locked"
bind_queue "notification-service.queue" "emergency.created"
bind_queue "notification-service.queue" "teleconsult.session_started"

# Nota: El reintento de 3 intentos se maneja en el consumer.py (contador en headers del mensaje),
# no en RabbitMQ nativo, ya que RabbitMQ no soporta x-max-retries de forma nativa.

echo "RabbitMQ inicializado."
