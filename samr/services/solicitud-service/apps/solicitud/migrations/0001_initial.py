import uuid
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Conversation", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("patient_id", models.UUIDField()), ("messages", models.JSONField(default=list)), ("created_at", models.DateTimeField(auto_now_add=True))], options={"db_table": "vity_conversations"}),
        migrations.CreateModel(name="FAQ", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("question", models.TextField()), ("answer", models.TextField()), ("updated_at", models.DateTimeField(auto_now=True))], options={"db_table": "faq_entries"}),
        migrations.CreateModel(name="Solicitud", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("patient_id", models.UUIDField()), ("sintomas", django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), default=list, size=None)),
            ("datos_biomedicos", models.JSONField(blank=True, default=dict)),
            ("fuente", models.CharField(choices=[("chatbot", "Chatbot"), ("iot_anomalia", "IoT anomaly"), ("manual", "Manual")], default="chatbot", max_length=20)),
            ("estado", models.CharField(choices=[("pendiente", "Pendiente"), ("validada", "Validada"), ("rechazada", "Rechazada"), ("pendiente_reintento", "Pendiente reintento")], default="pendiente", max_length=20)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"db_table": "solicitudes"}),
    ]
