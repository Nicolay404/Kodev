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
        assert response.status_code == 200 and AuditReview.objects.count() == 1

    def test_other_role_forbidden(self, api_client, auth_jwt_admin):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_admin}")
        assert api_client.get(reverse("audit_decisions")).status_code == 403

    def test_process_all_event(self):
        process_event("auth.login_success", {"usuario_id": None, "email": "x@test.com"})
        assert AuditLog.objects.get().event_type == "auth.login_success"
