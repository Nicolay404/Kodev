from celery import shared_task
from django.core.cache import cache
from apps.historial.models import Historial


@shared_task
def procesar_caso_cerrado(event_data):
    patient_id = event_data.get("patient_id")
    if not patient_id: return "ignored"
    history, _ = Historial.objects.get_or_create(patient_id=patient_id)
    if not any(item.get("caso_id") == event_data.get("caso_id") for item in history.eventos):
        history.eventos.append(event_data); history.save(update_fields=["eventos", "updated_at"])
    cache.delete(f"fhir:{patient_id}")
    return str(history.id)
