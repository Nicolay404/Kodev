from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar los db_table en 0001_initial.
    No-op en bases nuevas, donde las tablas ya nacen con el nombre correcto."""

    dependencies = [
        ("monitoring_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS monitoring_app_alert RENAME TO monitoring_alerts;",
            reverse_sql="ALTER TABLE IF EXISTS monitoring_alerts RENAME TO monitoring_app_alert;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS monitoring_app_vitalsign RENAME TO vital_signs;",
            reverse_sql="ALTER TABLE IF EXISTS vital_signs RENAME TO monitoring_app_vitalsign;",
        ),
    ]
