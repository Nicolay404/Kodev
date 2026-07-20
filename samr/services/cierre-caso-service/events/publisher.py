import pika
import json
import uuid
import datetime
import os

# Depender de settings o variables de entorno directamente para ser independiente
RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672//')
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'unknown-service')

def publicar_evento(routing_key: str, payload: dict):
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Garantizar que existe el exchange
    channel.exchange_declare(exchange='samr.events', exchange_type='topic', durable=True)

    event_body = {
        'event_id': str(uuid.uuid4()),
        'event_type': routing_key,
        'service_origin': SERVICE_NAME,
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'version': "1.0",
        'payload': payload
    }

    properties = pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
        content_type='application/json'
    )

    channel.basic_publish(
        exchange='samr.events',
        routing_key=routing_key,
        body=json.dumps(event_body),
        properties=properties
    )

    connection.close()
