import uuid
from django.db import models


class Emergency(models.Model):
    STATUS_CHOICES = (("pending", "Pending"), ("dispatched", "Dispatched"), ("closed", "Closed"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    triage_level = models.CharField(max_length=20)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "emergency_cases"


class FirstAidGuide(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emergency = models.ForeignKey(Emergency, related_name="guides", on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "guias_primeros_auxilios"
