from django.db import models

class Emergency(models.Model):
    STATUS_CHOICES = (
        ('reported', 'Reported'),
        ('dispatched', 'Dispatched'),
        ('resolved', 'Resolved'),
    )

    patient_id = models.IntegerField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    location = models.JSONField(default=dict)
    reported_at = models.DateTimeField(auto_now_add=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Emergency for patient {self.patient_id} - {self.status}"
