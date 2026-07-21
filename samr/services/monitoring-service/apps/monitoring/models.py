import uuid
from django.db import models


class VitalSign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.UUIDField()
    patient_id = models.UUIDField()
    value = models.JSONField()
    recorded_at = models.DateTimeField(auto_now_add=True)


class Alert(models.Model):
    SEVERITIES = (("critical", "Critical"), ("high", "High"), ("medium", "Medium"), ("low", "Low"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    severity = models.CharField(max_length=20, choices=SEVERITIES)
    created_at = models.DateTimeField(auto_now_add=True)
