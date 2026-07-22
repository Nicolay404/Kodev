from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar db_table='clinical_cases' en 0001_initial.
    No-op en bases nuevas, donde la tabla ya nace con el nombre correcto."""

    dependencies = [
        ("cierre_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS cierre_app_caso RENAME TO clinical_cases;",
            reverse_sql="ALTER TABLE IF EXISTS clinical_cases RENAME TO cierre_app_caso;",
        ),
    ]
