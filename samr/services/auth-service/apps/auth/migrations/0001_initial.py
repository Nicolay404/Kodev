import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("role", models.CharField(choices=[("patient", "Patient"), ("professional", "Professional"), ("nurse", "Nurse/Paramedic"), ("center_admin", "Center Admin"), ("system_admin", "System Admin"), ("dpd_delegate", "DPD Delegate")], default="patient", max_length=50)),
                ("failed_attempts", models.PositiveSmallIntegerField(default=0)),
                ("locked_until", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"abstract": False},
        )
    ]
