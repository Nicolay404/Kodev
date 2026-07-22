import uuid
from django.db import models


class AppendOnlyQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("audit_log es append-only")

    def delete(self):
        raise ValueError("audit_log es append-only")


class AuditLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    event_type = models.CharField(max_length=100)
    actor_id = models.UUIDField(null=True, blank=True)
    payload = models.JSONField()
    ai_confidence = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    ai_explainability = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = AppendOnlyQuerySet.as_manager()

    class Meta:
        db_table = "audit_log"

    def save(self, *args, **kwargs):
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists(): raise ValueError("audit_log es append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("audit_log es append-only")


class AuditReview(models.Model):
    STATES = (("pendiente", "Pendiente"), ("revisado", "Revisado"), ("observado", "Observado"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit_log_id = models.BigIntegerField()
    estado_revision = models.CharField(max_length=20, choices=STATES, default="pendiente")
    revisado_por = models.UUIDField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_reviews"
