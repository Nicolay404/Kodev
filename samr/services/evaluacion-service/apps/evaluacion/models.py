import uuid
from django.db import models


class Evaluacion(models.Model):
    LEVELS = (("critico", "Crítico"), ("alto", "Alto"), ("medio", "Medio"), ("bajo", "Bajo"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    solicitud_id = models.UUIDField(unique=True)
    nivel_riesgo = models.CharField(max_length=20, choices=LEVELS)
    fuentes_rag = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class Matching(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluacion = models.OneToOneField(Evaluacion, related_name="matching", on_delete=models.CASCADE)
    professional_id = models.UUIDField()
    center_id = models.UUIDField()
    score = models.DecimalField(max_digits=5, decimal_places=2)


class AvailableCenterCache(models.Model):
    center_id = models.UUIDField(primary_key=True)
    nombre = models.CharField(max_length=255)
    disponible = models.BooleanField(default=True)
