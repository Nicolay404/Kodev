from django.core.management.base import BaseCommand
from events.consumer import iniciar_consumidor
from tasks.procesar_historial import procesar_evento_clinico


class Command(BaseCommand):
    def handle(self, *args, **options):
        routing_keys = [
            "solicitud.validada", "riesgo.evaluado", "recursos.asignados",
            "teleconsult.session_started", "teleconsult.closed",
            "emergency.created", "emergency.dispatched", "caso.cerrado",
        ]
        iniciar_consumidor(
            "historial-interop-service.queue",
            routing_keys,
            lambda event_type, payload: procesar_evento_clinico.delay(event_type, payload),
        )
