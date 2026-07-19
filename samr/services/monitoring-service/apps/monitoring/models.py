from django.db import models

class IoTReading(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=255)
    patient_id = models.IntegerField()
    vitals = models.JSONField(default=dict)

    def __str__(self):
        return f"Reading from {self.device_id} at {self.timestamp}"

class Alert(models.Model):
    detectada_anomalia = models.BooleanField(default=True)
    patient_id = models.IntegerField()
    tipo = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert {self.tipo} for patient {self.patient_id}"
