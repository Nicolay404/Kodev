"""Consumidor común del bus de eventos de dominio SAMR."""

import json
import logging
import os

import pika

RABBITMQ_URL = os.environ.get(
    "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F"
)
logger = logging.getLogger(__name__)
REQUIRED_ENVELOPE_FIELDS = {
    "event_id",
    "event_type",
    "service_origin",
    "timestamp",
    "version",
    "payload",
}


def validar_envelope(evento: dict) -> None:
    missing = REQUIRED_ENVELOPE_FIELDS.difference(evento)
    if missing:
        raise ValueError(f"Envelope inválido; faltan: {', '.join(sorted(missing))}")
    if evento["version"] != "1.0" or not isinstance(evento["payload"], dict):
        raise ValueError("Versión o payload de evento inválido")


def iniciar_consumidor(queue_name: str, routing_keys: list[str], callback):
    """Consume eventos; RabbitMQ quorum limita a tres entregas antes del DLQ."""
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange="samr.events", exchange_type="topic", durable=True)
    channel.exchange_declare(
        exchange="samr.events.dlx", exchange_type="topic", durable=True
    )
    dlq_name = f"{queue_name}.dlq"
    channel.queue_declare(queue=dlq_name, durable=True)
    channel.queue_bind(
        queue=dlq_name, exchange="samr.events.dlx", routing_key=queue_name
    )
    channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={
            "x-queue-type": "quorum",
            "x-delivery-limit": 3,
            "x-dead-letter-exchange": "samr.events.dlx",
            "x-dead-letter-routing-key": queue_name,
        },
    )
    for routing_key in routing_keys:
        channel.queue_bind(
            exchange="samr.events", queue=queue_name, routing_key=routing_key
        )

    def on_message(ch, method, properties, body):
        try:
            evento = json.loads(body)
            validar_envelope(evento)
            callback(evento["event_type"], evento["payload"])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception("Error procesando evento en %s", queue_name)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    try:
        logger.info("Esperando eventos en %s", queue_name)
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        if connection.is_open:
            connection.close()
