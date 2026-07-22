from celery import shared_task
from django.core.cache import cache
from apps.historial.models import Historial


def _event_key(event_type, event_data):
    source_id = next(
        (
            event_data.get(key)
            for key in ("caso_id", "session_id", "emergency_id", "matching_id", "evaluacion_id", "solicitud_id")
            if event_data.get(key)
        ),
        None,
    )
    return f"{event_type}:{source_id}" if source_id else None


@shared_task
def procesar_evento_clinico(event_type, event_data):
    patient_id = event_data.get("patient_id")
    if not patient_id:
        return "ignored"
    history, _ = Historial.objects.get_or_create(patient_id=patient_id)
    event_key = _event_key(event_type, event_data)
    if event_key and any(item.get("event_key") == event_key for item in history.eventos):
        return str(history.id)
    history.eventos.append({"event_type": event_type, "event_key": event_key, **event_data})
    history.save(update_fields=["eventos", "updated_at"])
    cache.delete(f"fhir:{patient_id}")
    return str(history.id)


@shared_task
def procesar_caso_cerrado(event_data):
    return procesar_evento_clinico("caso.cerrado", event_data)
