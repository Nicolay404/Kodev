import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Historial", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("patient_id", models.UUIDField(unique=True)), ("eventos", models.JSONField(default=list)), ("updated_at", models.DateTimeField(auto_now=True))], options={"db_table": "expedientes_consolidados"})]
