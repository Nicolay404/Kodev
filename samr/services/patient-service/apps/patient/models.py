import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True)
    cedula_encrypted = models.BinaryField()
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = ArrayField(models.TextField(), default=list, blank=True)
    chronic_conditions = ArrayField(models.TextField(), default=list, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    consent_data = models.BooleanField(default=False)
    consent_ai = models.BooleanField(default=False)
    consent_sharing = models.BooleanField(default=False)

    class Meta:
        db_table = "patients"

    def __str__(self):
        return str(self.id)
