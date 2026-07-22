from celery import shared_task
from apps.audit.models import AuditLog


SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token", "reset_token", "authorization"}


def redact_sensitive(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else redact_sensitive(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value


@shared_task
def process_event(event_type, payload):
    actor = payload.get("actor_id") or payload.get("usuario_id")
    audit_payload = redact_sensitive(payload.get("payload", payload))
    return AuditLog.objects.create(event_type=event_type, actor_id=actor or None, payload=audit_payload, ai_confidence=payload.get("ai_confidence"), ai_explainability=payload.get("ai_explainability")).id


procesar_riesgo_evaluado = lambda event_data: process_event("riesgo.evaluado", event_data)
