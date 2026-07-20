from django.core.management.base import BaseCommand
from apps.solicitud.models import Solicitud
from events.consumer import iniciar_consumidor
from events.publisher import publicar_evento
from tasks.validate_with_consortium import validate_with_consortium


class Command(BaseCommand):
    help = "Crea solicitudes automáticas ante anomalías IoT críticas"

    def handle(self, *args, **options):
        def callback(event_type, payload):
            if event_type != "vitals.critical_detected":
                return
            solicitud = Solicitud.objects.create(
                patient_id=payload["patient_id"],
                sintomas=payload.get("anomalies", []),
                datos_biomedicos=payload.get("value", {}),
                fuente="iot_anomalia",
            )
            publicar_evento("solicitud.creada", {
                "solicitud_id": str(solicitud.id), "patient_id": str(solicitud.patient_id),
                "sintomas": solicitud.sintomas, "fuente": solicitud.fuente,
            })
            validate_with_consortium.delay(str(solicitud.id))
        iniciar_consumidor("solicitud-service.queue", ["vitals.critical_detected"], callback)
