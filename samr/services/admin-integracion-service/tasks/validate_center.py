from celery import shared_task
from django.conf import settings
from apps.admin_integ.models import Center
from events.publisher import publicar_evento


@shared_task
def validate_center_m2m(center_id):
    center = Center.objects.filter(id=center_id).first()
    if not center: return "not_found"
    accepted = settings.MVP_CENTER_VALIDATION_OUTCOME == "validated"
    center.status = "validated" if accepted else "rejected"; center.save(update_fields=["status"])
    event = "center.validated" if accepted else "center.rejected"
    publicar_evento(event, {"center_id": str(center.id), "nombre": center.name, "motivo": None if accepted else "Rechazo configurado en simulador MVP"})
    return center.status
