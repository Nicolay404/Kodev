from django.db import models

class Patient(models.Model):
    user_id = models.IntegerField(unique=True) # Referencia al id en auth-service
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.CharField(max_length=50)
    allergies = models.JSONField(default=list)
    chronic_conditions = models.JSONField(default=list)
    geolocation = models.JSONField(default=dict)
    gdpr_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

class PatientMedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, related_name='medical_history', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} - {self.event_type}"
