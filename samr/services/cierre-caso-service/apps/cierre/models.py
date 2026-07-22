import uuid
from django.db import models


class Caso(models.Model):
    STATUS_CHOICES = (("open", "Open"), ("closed", "Closed"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    teleconsult_id = models.UUIDField(null=True, blank=True)
    emergency_id = models.UUIDField(null=True, blank=True)
    clinical_notes = models.TextField(blank=True)
    integrity_hash = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "clinical_cases"
