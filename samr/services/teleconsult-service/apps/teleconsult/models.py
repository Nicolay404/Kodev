import secrets
import uuid
from django.db import models


def room_token(): return secrets.token_urlsafe(32)[:64]


class TeleconsultSession(models.Model):
    STATUS_CHOICES = (("active", "Active"), ("closed", "Closed"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    professional_id = models.UUIDField()
    emergency_id = models.UUIDField(null=True, blank=True)
    room_token = models.CharField(max_length=64, unique=True, default=room_token, editable=False)
    diagnosis = models.TextField(blank=True)
    ai_recommendation = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "teleconsults"
