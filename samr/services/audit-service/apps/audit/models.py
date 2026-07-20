from django.db import models

class DecisionIA(models.Model):
    # Campos base de auditoría inmutable (append-only)
    solicitud_id = models.IntegerField()
    evaluacion_id = models.IntegerField(null=True, blank=True)
    decision = models.JSONField()
    context = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Campos de revisión por DPD (Delegado de Protección de Datos)
    reviewed = models.BooleanField(default=False)
    review_notes = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Audit Log {self.id} (Solicitud {self.solicitud_id})"
