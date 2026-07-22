from unittest.mock import patch
import pytest
from django.urls import reverse
from apps.audit.models import AuditLog, AuditReview
from tasks.procesar_auditoria import process_event


@pytest.mark.django_db
class TestAuditAPI:
    def test_dpd_reads_and_reviews(self, api_client, auth_jwt_dpd):
        log = AuditLog.objects.create(event_type="riesgo.evaluado", payload={"risk": "medio"})
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_dpd}")
        assert api_client.get(reverse("audit_decisions")).status_code == 200
        response = api_client.patch(reverse("audit_review", kwargs={"audit_log_id": log.id}), {"estado_revision": "revisado", "comentario": "Conforme"}, format="json")
        second = api_client.patch(reverse("audit_review", kwargs={"audit_log_id": log.id}), {"estado_revision": "observado", "comentario": "Seguimiento"}, format="json")
        assert response.status_code == 200 and second.status_code == 200 and AuditReview.objects.count() == 2

    def test_other_role_forbidden(self, api_client, auth_jwt_admin):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_admin}")
        assert api_client.get(reverse("audit_decisions")).status_code == 403

    def test_process_all_event(self):
        process_event("auth.login_success", {"usuario_id": None, "email": "x@test.com"})
        assert AuditLog.objects.get().event_type == "auth.login_success"

    def test_sensitive_event_fields_are_redacted(self):
        process_event("auth.password_reset_requested", {"usuario_id": None, "reset_token": "secret", "nested": {"access_token": "secret"}})
        payload = AuditLog.objects.get().payload
        assert payload["reset_token"] == "[REDACTED]"
        assert payload["nested"]["access_token"] == "[REDACTED]"

    def test_filters_and_paginates_decisions(self, api_client, auth_jwt_dpd):
        AuditLog.objects.create(event_type="riesgo.evaluado", payload={})
        AuditLog.objects.create(event_type="auth.login_success", payload={})
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_dpd}")
        response = api_client.get(reverse("audit_decisions"), {"event_type": "riesgo.evaluado", "limit": 1})
        assert response.status_code == 200 and len(response.data) == 1
        assert response.data[0]["event_type"] == "riesgo.evaluado"

    def test_audit_log_cannot_be_updated_or_deleted(self):
        log = AuditLog.objects.create(event_type="auth.login_success", payload={})
        with pytest.raises(ValueError):
            AuditLog.objects.filter(id=log.id).update(event_type="changed")
        with pytest.raises(ValueError):
            log.delete()
