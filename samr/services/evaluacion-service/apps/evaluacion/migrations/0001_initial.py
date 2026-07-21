import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="AvailableCenterCache", fields=[("center_id", models.UUIDField(primary_key=True, serialize=False)), ("nombre", models.CharField(max_length=255)), ("disponible", models.BooleanField(default=True))]),
        migrations.CreateModel(name="Evaluacion", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("solicitud_id", models.UUIDField(unique=True)), ("nivel_riesgo", models.CharField(choices=[("critico", "Crítico"), ("alto", "Alto"), ("medio", "Medio"), ("bajo", "Bajo")], max_length=20)), ("fuentes_rag", models.JSONField(default=list)), ("created_at", models.DateTimeField(auto_now_add=True))]),
        migrations.CreateModel(name="Matching", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("professional_id", models.UUIDField()), ("center_id", models.UUIDField()), ("score", models.DecimalField(decimal_places=2, max_digits=5)), ("evaluacion", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="matching", to="evaluacion_app.evaluacion"))]),
    ]
