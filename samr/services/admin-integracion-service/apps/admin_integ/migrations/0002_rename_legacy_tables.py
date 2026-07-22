from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar los db_table en 0001_initial.
    No-op en bases nuevas, donde las tablas ya nacen con el nombre correcto."""

    dependencies = [
        ("admin_integ_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS admin_integ_app_center RENAME TO centers;",
            reverse_sql="ALTER TABLE IF EXISTS centers RENAME TO admin_integ_app_center;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS admin_integ_app_device RENAME TO devices;",
            reverse_sql="ALTER TABLE IF EXISTS devices RENAME TO admin_integ_app_device;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS admin_integ_app_professional RENAME TO professionals;",
            reverse_sql="ALTER TABLE IF EXISTS professionals RENAME TO admin_integ_app_professional;",
        ),
    ]
