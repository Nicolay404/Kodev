import pika
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Verifica la conectividad de notification-service con RabbitMQ."
    requires_system_checks = []

    def handle(self, *args, **options):
        connection = None
        try:
            parameters = pika.URLParameters(settings.RABBITMQ_URL)
            parameters.socket_timeout = 5
            parameters.blocked_connection_timeout = 5
            connection = pika.BlockingConnection(parameters)
            if not connection.is_open:
                raise RuntimeError("RabbitMQ no abrió la conexión")
        except Exception as exc:
            raise CommandError(f"health check fallido: {exc}") from exc
        finally:
            if connection is not None and connection.is_open:
                connection.close()
        self.stdout.write("ok")
