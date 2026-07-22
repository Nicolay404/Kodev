from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar db_table='teleconsults' en 0001_initial.
    No-op en bases nuevas, donde la tabla ya nace con el nombre correcto."""

    dependencies = [
        ("teleconsult_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS teleconsult_app_teleconsultsession RENAME TO teleconsults;",
            reverse_sql="ALTER TABLE IF EXISTS teleconsults RENAME TO teleconsult_app_teleconsultsession;",
        ),
    ]
