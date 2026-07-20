from django.db import models

class Historial(models.Model):
    patient_id = models.IntegerField(unique=True)
    data = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Historial of Patient {self.patient_id}"

class Consentimiento(models.Model):
    patient_id = models.IntegerField(unique=True)
    fhir_enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consent Patient {self.patient_id}: {self.fhir_enabled}"
