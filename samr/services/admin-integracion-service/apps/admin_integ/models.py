from django.db import models

class Center(models.Model):
    name = models.CharField(max_length=255)
    location = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    max_capacity = models.IntegerField(default=0)
    current_occupancy = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Cap: {self.current_occupancy}/{self.max_capacity}"

class Device(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)
    patient_id = models.IntegerField()
    device_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Device {self.mac_address} (Patient {self.patient_id})"
