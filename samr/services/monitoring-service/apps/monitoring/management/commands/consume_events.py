from django.core.management.base import BaseCommand
from events.consumer import iniciar_consumidor
from apps.monitoring.services import register_device


class Command(BaseCommand):
    help = "Consume device.registered para habilitar ingesta IoT"

    def handle(self, *args, **options):
        def callback(event_type, payload):
            if event_type == "device.registered":
                register_device(payload)
        iniciar_consumidor("monitoring-service.queue", ["device.registered"], callback)
