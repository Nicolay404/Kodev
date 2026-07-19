from django.db import models

class Conversation(models.Model):
    patient_id = models.IntegerField()
    messages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

class Solicitud(models.Model):
    STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('validada', 'Validada'),
        ('rechazada', 'Rechazada'),
        ('pendiente_reintento', 'Pendiente Reintento'),
    )
    URGENCY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    patient_id = models.IntegerField()
    description = models.TextField()
    symptoms = models.JSONField(default=list)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    estado = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pendiente')
    consorcio_validation_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ConsorcioValidationLog(models.Model):
    solicitud = models.ForeignKey(Solicitud, related_name='validation_logs', on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
