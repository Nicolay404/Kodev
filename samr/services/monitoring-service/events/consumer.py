import pika
import json
import os
import logging

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672//')
logger = logging.getLogger(__name__)

def iniciar_consumidor(queue_name: str, routing_keys: list[str], callback):
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declarar exchanges
    channel.exchange_declare(exchange='samr.events', exchange_type='topic', durable=True)
    channel.exchange_declare(exchange='samr.events.dlx', exchange_type='topic', durable=True)

    # Declarar cola
    channel.queue_declare(
        queue=queue_name, 
        durable=True, 
        arguments={'x-dead-letter-exchange': 'samr.events.dlx'}
    )

    # Bindings
    for rk in routing_keys:
        channel.queue_bind(exchange='samr.events', queue=queue_name, routing_key=rk)

    def on_message_callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            # Manejar límite de reintentos aquí (incrementando headers['x-retry-count'])
            # antes de enviar a callback o propagar excepción
            callback(message['payload'])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error procesando mensaje de cola {queue_name}: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback)

    try:
        logger.info(f"[*] Esperando eventos en {queue_name}. Para salir presione CTRL+C")
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()
