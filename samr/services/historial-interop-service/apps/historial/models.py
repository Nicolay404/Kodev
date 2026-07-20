import uuid
from django.db import models


class Historial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField(unique=True)
    eventos = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)
