import uuid
import apps.teleconsult.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="TeleconsultSession", fields=[
        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
        ("patient_id", models.UUIDField()), ("professional_id", models.UUIDField()),
        ("emergency_id", models.UUIDField(blank=True, null=True)),
        ("room_token", models.CharField(default=apps.teleconsult.models.room_token, editable=False, max_length=64, unique=True)),
        ("diagnosis", models.TextField(blank=True)), ("ai_recommendation", models.JSONField(blank=True, default=dict)),
        ("status", models.CharField(choices=[("active", "Active"), ("closed", "Closed")], default="active", max_length=20)),
        ("closed_at", models.DateTimeField(blank=True, null=True)),
    ], options={"db_table": "teleconsults"})]
