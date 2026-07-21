import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Alert", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("patient_id", models.UUIDField()), ("severity", models.CharField(choices=[("critical", "Critical"), ("high", "High"), ("medium", "Medium"), ("low", "Low")], max_length=20)), ("created_at", models.DateTimeField(auto_now_add=True))]),
        migrations.CreateModel(name="VitalSign", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("device_id", models.UUIDField()), ("patient_id", models.UUIDField()), ("value", models.JSONField()), ("recorded_at", models.DateTimeField(auto_now_add=True))]),
    ]
