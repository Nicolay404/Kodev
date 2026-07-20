from celery import shared_task
from apps.audit.models import AuditLog


@shared_task
def process_event(event_type, payload):
    actor = payload.get("actor_id") or payload.get("usuario_id")
    return AuditLog.objects.create(event_type=event_type, actor_id=actor or None, payload=payload.get("payload", payload), ai_confidence=payload.get("ai_confidence"), ai_explainability=payload.get("ai_explainability")).id


procesar_riesgo_evaluado = lambda event_data: process_event("riesgo.evaluado", event_data)
