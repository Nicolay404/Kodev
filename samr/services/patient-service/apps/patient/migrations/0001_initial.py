import uuid
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Patient", fields=[
        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
        ("user_id", models.UUIDField(unique=True)),
        ("cedula_encrypted", models.BinaryField()),
        ("blood_type", models.CharField(blank=True, max_length=5)),
        ("allergies", django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, size=None)),
        ("chronic_conditions", django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, size=None)),
        ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        ("consent_data", models.BooleanField(default=False)),
        ("consent_ai", models.BooleanField(default=False)),
        ("consent_sharing", models.BooleanField(default=False)),
    ], options={"db_table": "patients"})]
