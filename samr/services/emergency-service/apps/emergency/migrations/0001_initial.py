import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Emergency", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("patient_id", models.UUIDField()), ("triage_level", models.CharField(max_length=20)), ("status", models.CharField(choices=[("pending", "Pending"), ("dispatched", "Dispatched"), ("closed", "Closed")], default="pending", max_length=30)), ("created_at", models.DateTimeField(auto_now_add=True))], options={"db_table": "emergency_cases"}),
        migrations.CreateModel(name="FirstAidGuide", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("contenido", models.TextField()), ("fecha_generacion", models.DateTimeField(auto_now_add=True)), ("emergency", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="guides", to="emergency_app.emergency"))], options={"db_table": "guias_primeros_auxilios"}),
    ]
