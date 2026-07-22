import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Caso", fields=[
        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
        ("patient_id", models.UUIDField()), ("teleconsult_id", models.UUIDField(blank=True, null=True)),
        ("emergency_id", models.UUIDField(blank=True, null=True)), ("clinical_notes", models.TextField(blank=True)),
        ("integrity_hash", models.CharField(blank=True, max_length=64)),
        ("status", models.CharField(choices=[("open", "Open"), ("closed", "Closed")], default="open", max_length=20)),
        ("closed_at", models.DateTimeField(blank=True, null=True)),
    ], options={"db_table": "clinical_cases"})]
