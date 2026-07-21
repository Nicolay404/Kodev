from django.core.management.base import BaseCommand
from apps.cierre.models import Caso
from events.consumer import iniciar_consumidor


class Command(BaseCommand):
    help = "Abre casos clínicos desde atenciones M3"
    def handle(self, *args, **options):
        def callback(event_type, payload):
            if event_type == "teleconsult.closed":
                Caso.objects.get_or_create(teleconsult_id=payload["session_id"], defaults={"patient_id": payload["patient_id"], "clinical_notes": payload.get("diagnosis", "")})
            elif event_type == "emergency.dispatched":
                Caso.objects.get_or_create(emergency_id=payload["emergency_id"], defaults={"patient_id": payload["patient_id"]})
        iniciar_consumidor("cierre-caso-service.queue", ["teleconsult.closed", "emergency.dispatched"], callback)
