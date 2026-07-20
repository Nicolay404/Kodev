"""Publicador común del bus de eventos de dominio SAMR."""

import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pika

RABBITMQ_URL = os.environ.get(
    "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F"
)
SERVICE_NAME = os.environ.get("SERVICE_NAME", "unknown-service")


def _json_default(value):
    if isinstance(value, (uuid.UUID, Decimal)):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Tipo no serializable en evento: {type(value).__name__}")


def construir_evento(routing_key: str, payload: dict) -> dict:
    if not routing_key or not isinstance(payload, dict):
        raise ValueError("routing_key y payload dict son obligatorios")
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": routing_key,
        "service_origin": SERVICE_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "payload": payload,
    }


def publicar_evento(routing_key: str, payload: dict) -> str:
    """Publica de forma persistente y confirma que RabbitMQ recibió el evento."""
    evento = construir_evento(routing_key, payload)
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    try:
        channel = connection.channel()
        channel.exchange_declare(
            exchange="samr.events", exchange_type="topic", durable=True
        )
        channel.confirm_delivery()
        channel.basic_publish(
            exchange="samr.events",
            routing_key=routing_key,
            body=json.dumps(evento, default=_json_default),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                content_type="application/json",
                content_encoding="utf-8",
                message_id=evento["event_id"],
                type=routing_key,
            ),
            mandatory=True,
        )
        return evento["event_id"]
    finally:
        if connection.is_open:
            connection.close()
