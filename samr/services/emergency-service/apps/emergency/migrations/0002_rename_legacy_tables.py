from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar los db_table en 0001_initial.
    No-op en bases nuevas, donde las tablas ya nacen con el nombre correcto."""

    dependencies = [
        ("emergency_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS emergency_app_emergency RENAME TO emergency_cases;",
            reverse_sql="ALTER TABLE IF EXISTS emergency_cases RENAME TO emergency_app_emergency;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS emergency_app_firstaidguide RENAME TO guias_primeros_auxilios;",
            reverse_sql="ALTER TABLE IF EXISTS guias_primeros_auxilios RENAME TO emergency_app_firstaidguide;",
        ),
    ]
