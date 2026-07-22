from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar los db_table en 0001_initial.
    No-op en bases nuevas, donde las tablas ya nacen con el nombre correcto."""

    dependencies = [
        ("evaluacion_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS evaluacion_app_availablecentercache RENAME TO centros_disponibles_cache;",
            reverse_sql="ALTER TABLE IF EXISTS centros_disponibles_cache RENAME TO evaluacion_app_availablecentercache;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS evaluacion_app_evaluacion RENAME TO evaluaciones_riesgo;",
            reverse_sql="ALTER TABLE IF EXISTS evaluaciones_riesgo RENAME TO evaluacion_app_evaluacion;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS evaluacion_app_matching RENAME TO matchings;",
            reverse_sql="ALTER TABLE IF EXISTS matchings RENAME TO evaluacion_app_matching;",
        ),
    ]
