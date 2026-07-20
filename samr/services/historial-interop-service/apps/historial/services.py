import requests
from django.conf import settings
from django.core.cache import cache


def verify_sharing_consent(patient_id):
    response = requests.get(f"{settings.PATIENT_SERVICE_URL}/api/patients/{patient_id}/summary/", headers={"X-Service-Token": settings.SERVICE_TOKEN}, timeout=5)
    response.raise_for_status()
    return bool(response.json().get("consent_sharing"))


def compose_fhir_bundle(history):
    key = f"fhir:{history.patient_id}"
    cached = cache.get(key)
    if cached: return cached
    bundle = {"resourceType": "Bundle", "id": str(history.id), "type": "collection", "entry": []}
    for event in history.eventos:
        resource = {"resourceType": "Encounter", "id": str(event.get("caso_id", "")), "status": "finished", "subject": {"reference": f"Patient/{history.patient_id}"}, "period": {"end": event.get("closed_at")}}
        bundle["entry"].append({"resource": resource})
    cache.set(key, bundle, timeout=300)
    return bundle
