import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    messages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vity_conversations"


class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    answer = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "faq_entries"

    def __str__(self):
        return self.question


class Solicitud(models.Model):
    STATUS_CHOICES = (("pendiente", "Pendiente"), ("validada", "Validada"), ("rechazada", "Rechazada"), ("pendiente_reintento", "Pendiente reintento"))
    SOURCE_CHOICES = (("chatbot", "Chatbot"), ("iot_anomalia", "IoT anomaly"), ("manual", "Manual"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    sintomas = ArrayField(models.TextField(), default=list)
    datos_biomedicos = models.JSONField(default=dict, blank=True)
    fuente = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="chatbot")
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendiente")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "solicitudes"
