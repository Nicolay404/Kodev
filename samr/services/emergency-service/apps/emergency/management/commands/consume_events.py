from django.core.management.base import BaseCommand
from apps.emergency.views import create_emergency
from events.consumer import iniciar_consumidor


class Command(BaseCommand):
    help = "Activa emergencias a partir de escalamiento o signos críticos"
    def handle(self, *args, **options):
        def callback(event_type, payload):
            if event_type in {"vity.escalation_requested", "vitals.critical_detected"}:
                create_emergency(payload["patient_id"], payload.get("nivel_riesgo", "critico"))
        iniciar_consumidor("emergency-service.queue", ["vity.escalation_requested", "vitals.critical_detected"], callback)
