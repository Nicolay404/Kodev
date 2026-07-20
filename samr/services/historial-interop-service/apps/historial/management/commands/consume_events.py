from django.core.management.base import BaseCommand
from events.consumer import iniciar_consumidor
from tasks.procesar_historial import procesar_caso_cerrado


class Command(BaseCommand):
    def handle(self, *args, **options):
        iniciar_consumidor("historial-interop-service.queue", ["caso.cerrado"], lambda event_type, payload: procesar_caso_cerrado.delay(payload))
