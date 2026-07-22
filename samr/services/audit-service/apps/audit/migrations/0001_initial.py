import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True; dependencies = []
    operations = [
        migrations.CreateModel(name="AuditLog", fields=[("id", models.BigAutoField(primary_key=True, serialize=False)), ("event_type", models.CharField(max_length=100)), ("actor_id", models.UUIDField(blank=True, null=True)), ("payload", models.JSONField()), ("ai_confidence", models.DecimalField(blank=True, decimal_places=3, max_digits=4, null=True)), ("ai_explainability", models.JSONField(blank=True, null=True)), ("created_at", models.DateTimeField(auto_now_add=True))], options={"db_table": "audit_log"}),
        migrations.CreateModel(name="AuditReview", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("audit_log_id", models.BigIntegerField(unique=True)), ("estado_revision", models.CharField(choices=[("pendiente", "Pendiente"), ("revisado", "Revisado"), ("observado", "Observado")], default="pendiente", max_length=20)), ("revisado_por", models.UUIDField(blank=True, null=True)), ("comentario", models.TextField(blank=True, null=True)), ("fecha_revision", models.DateTimeField(blank=True, null=True)), ("created_at", models.DateTimeField(auto_now_add=True))], options={"db_table": "audit_reviews"}),
    ]
