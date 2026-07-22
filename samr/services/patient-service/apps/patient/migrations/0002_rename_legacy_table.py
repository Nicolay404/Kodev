from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar db_table='patients' en 0001_initial.
    No-op en bases nuevas, donde la tabla ya nace con el nombre correcto."""

    dependencies = [
        ("patient_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS patient_app_patient RENAME TO patients;",
            reverse_sql="ALTER TABLE IF EXISTS patients RENAME TO patient_app_patient;",
        ),
    ]
