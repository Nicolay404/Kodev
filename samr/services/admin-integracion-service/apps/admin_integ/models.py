import uuid
from django.db import models


class Center(models.Model):
    STATES = (("pending_validation", "Pending validation"), ("validated", "Validated"), ("rejected", "Rejected"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATES, default="pending_validation")

    class Meta:
        db_table = "centers"


class Professional(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    available = models.BooleanField(default=True)
    current_load = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "professionals"


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    device_type = models.CharField(max_length=50)
    registered_by = models.UUIDField()
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "devices"
