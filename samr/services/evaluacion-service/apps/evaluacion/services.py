"""Adaptadores deterministas del MVP; no constituyen decisión clínica."""
from decimal import Decimal
import requests
from django.conf import settings
from .models import AvailableCenterCache


def evaluate_risk(solicitud_data: dict) -> dict:
    text = " ".join(solicitud_data.get("sintomas", [])).lower()
    level = settings.MVP_DEFAULT_RISK_LEVEL
    if any(term and term in text for term in settings.MVP_CRITICAL_TERMS):
        level = "critico"
    elif any(term and term in text for term in settings.MVP_HIGH_TERMS):
        level = "alto"
    return {
        "nivel_riesgo": level,
        "fuentes_rag": [{"source": "mvp_rules", "version": "1.0", "clinical_validation": False}],
        "explainability": {"adapter": "mvp_keyword_rules", "clinical_validation": False},
    }


def has_ai_consent(patient_id):
    response = requests.get(
        f"{settings.PATIENT_SERVICE_URL}/api/patients/{patient_id}/summary/",
        headers={"X-Service-Token": settings.SERVICE_TOKEN},
        timeout=5,
    )
    if response.status_code == 404:
        return False
    response.raise_for_status()
    return response.json().get("consent_ai") is True


def find_best_center(center_id=None):
    centers = AvailableCenterCache.objects.filter(disponible=True)
    if center_id:
        return centers.filter(center_id=center_id).first()
    return centers.order_by("nombre", "center_id").first()


def mvp_matching_score():
    return Decimal("100.00")


def update_center_cache(event_type, payload):
    if event_type == "center.validated":
        AvailableCenterCache.objects.update_or_create(center_id=payload["center_id"], defaults={"nombre": payload["nombre"], "disponible": True})
    elif event_type == "center.rejected":
        AvailableCenterCache.objects.filter(center_id=payload["center_id"]).update(disponible=False)
