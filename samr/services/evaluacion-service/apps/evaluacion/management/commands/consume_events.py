from django.core.management.base import BaseCommand
from apps.evaluacion.services import update_center_cache
from events.consumer import iniciar_consumidor
from tasks.procesar_solicitud import procesar_solicitud_validada


class Command(BaseCommand):
    help = "Consume solicitudes validadas y cambios del catálogo M4"
    def handle(self, *args, **options):
        def callback(event_type, payload):
            if event_type == "solicitud.validada": procesar_solicitud_validada.delay(payload)
            elif event_type in {"center.validated", "center.rejected"}: update_center_cache(event_type, payload)
        iniciar_consumidor("evaluacion-service.queue", ["solicitud.validada", "center.validated", "center.rejected"], callback)
