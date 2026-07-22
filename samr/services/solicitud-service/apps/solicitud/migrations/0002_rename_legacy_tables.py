from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar los db_table en 0001_initial.
    No-op en bases nuevas, donde las tablas ya nacen con el nombre correcto."""

    dependencies = [
        ("solicitud_app", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS solicitud_app_conversation RENAME TO vity_conversations;",
            reverse_sql="ALTER TABLE IF EXISTS vity_conversations RENAME TO solicitud_app_conversation;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS solicitud_app_faq RENAME TO faq_entries;",
            reverse_sql="ALTER TABLE IF EXISTS faq_entries RENAME TO solicitud_app_faq;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS solicitud_app_solicitud RENAME TO solicitudes;",
            reverse_sql="ALTER TABLE IF EXISTS solicitudes RENAME TO solicitud_app_solicitud;",
        ),
    ]
