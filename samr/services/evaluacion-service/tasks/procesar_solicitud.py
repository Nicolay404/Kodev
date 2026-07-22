from celery import shared_task
from requests import RequestException
from apps.evaluacion.models import Evaluacion
from apps.evaluacion.services import evaluate_risk, has_ai_consent
from events.publisher import publicar_evento


@shared_task(autoretry_for=(RequestException,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def procesar_solicitud_validada(solicitud_data):
    solicitud_id = solicitud_data.get("solicitud_id")
    if not solicitud_id or Evaluacion.objects.filter(solicitud_id=solicitud_id).exists():
        return "ignored"
    if not solicitud_data.get("patient_id") or not has_ai_consent(solicitud_data["patient_id"]):
        return "consent_required"
    result = evaluate_risk(solicitud_data)
    evaluacion = Evaluacion.objects.create(solicitud_id=solicitud_id, nivel_riesgo=result["nivel_riesgo"], fuentes_rag=result["fuentes_rag"])
    payload = {
        "evaluacion_id": str(evaluacion.id),
        "solicitud_id": str(evaluacion.solicitud_id),
        "patient_id": solicitud_data.get("patient_id"),
        "nivel_riesgo": evaluacion.nivel_riesgo,
        "fuentes_rag": evaluacion.fuentes_rag,
    }
    publicar_evento("riesgo.evaluado", payload)
    publicar_evento("ai.decision_logged", {"decision_type": "risk_evaluation", "actor_id": None, "payload": payload, "ai_confidence": None, "ai_explainability": result["explainability"]})
    if evaluacion.nivel_riesgo == "critico":
        publicar_evento("vity.escalation_requested", payload)
    return str(evaluacion.id)
