from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar db_table='expedientes_consolidados' en 0001_initial.
    No-op en bases nuevas, donde la tabla ya nace con el nombre correcto."""

    dependencies = [
        ("historial_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS historial_app_historial RENAME TO expedientes_consolidados;",
            reverse_sql="ALTER TABLE IF EXISTS expedientes_consolidados RENAME TO historial_app_historial;",
        ),
    ]
