from django.core.management.base import BaseCommand
from apps.teleconsult.models import TeleconsultSession
from apps.teleconsult.views import publish_started
from events.consumer import iniciar_consumidor


class Command(BaseCommand):
    help = "Inicia teleconsultas asignadas por M2"
    def handle(self, *args, **options):
        def callback(event_type, payload):
            if event_type != "recursos.asignados": return
            session = TeleconsultSession.objects.create(patient_id=payload["patient_id"], professional_id=payload["professional_id"])
            publish_started(session)
        iniciar_consumidor("teleconsult-service.queue", ["recursos.asignados"], callback)
