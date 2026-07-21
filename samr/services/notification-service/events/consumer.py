"""Consumidor RabbitMQ del servicio reactivo de notificaciones."""

import json
import logging
import os

import pika

logger = logging.getLogger(__name__)
REQUIRED_FIELDS = {
    "event_id", "event_type", "service_origin", "timestamp", "version", "payload"
}


def iniciar_consumidor(queue_name, routing_keys, callback):
    connection = pika.BlockingConnection(
        pika.URLParameters(
            os.environ.get(
                "RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F"
            )
        )
    )
    channel = connection.channel()
    channel.exchange_declare(
        exchange="samr.events", exchange_type="topic", durable=True
    )
    channel.exchange_declare(
        exchange="samr.events.dlx", exchange_type="topic", durable=True
    )
    dlq_name = f"{queue_name}.dlq"
    channel.queue_declare(queue=dlq_name, durable=True)
    channel.queue_bind(
        exchange="samr.events.dlx", queue=dlq_name, routing_key=queue_name
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
    for key in routing_keys:
        channel.queue_bind(exchange="samr.events", queue=queue_name, routing_key=key)

    def consume(ch, method, properties, body):
        try:
            event = json.loads(body)
            if REQUIRED_FIELDS.difference(event) or event["version"] != "1.0":
                raise ValueError("Envelope de evento invalido")
            callback(event["event_type"], event["payload"])
            ch.basic_ack(method.delivery_tag)
        except Exception:
            logger.exception("Fallo al procesar notificacion")
            ch.basic_nack(method.delivery_tag, requeue=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=consume)
    channel.start_consuming()
