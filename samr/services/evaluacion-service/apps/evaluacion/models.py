from django.db import models

class Evaluacion(models.Model):
    solicitud_id = models.IntegerField(unique=True)
    riesgo_score = models.FloatField(default=0.0)
    recomendaciones = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Matching(models.Model):
    evaluacion = models.OneToOneField(Evaluacion, related_name='matching', on_delete=models.CASCADE)
    centro_asignado = models.CharField(max_length=255)
    recursos = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
