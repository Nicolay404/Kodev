from django.core.management.base import BaseCommand
from events.consumer import iniciar_consumidor
from tasks.procesar_auditoria import process_event


class Command(BaseCommand):
    def handle(self, *args, **options):
        iniciar_consumidor("audit-service.queue", ["#"], lambda event_type, payload: process_event.delay(event_type, payload))
