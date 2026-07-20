import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True; dependencies = []
    operations = [
        migrations.CreateModel(name="Center", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("name", models.CharField(max_length=255)), ("type", models.CharField(blank=True, max_length=50)), ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)), ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)), ("status", models.CharField(choices=[("pending_validation", "Pending validation"), ("validated", "Validated"), ("rejected", "Rejected")], default="pending_validation", max_length=20))]),
        migrations.CreateModel(name="Device", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("patient_id", models.UUIDField()), ("device_type", models.CharField(max_length=50)), ("registered_by", models.UUIDField()), ("active", models.BooleanField(default=True))]),
        migrations.CreateModel(name="Professional", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("specialty", models.CharField(max_length=100)), ("available", models.BooleanField(default=True)), ("current_load", models.PositiveSmallIntegerField(default=0)), ("center", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="admin_integ_app.center"))]),
    ]
