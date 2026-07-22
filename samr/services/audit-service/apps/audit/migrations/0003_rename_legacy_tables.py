from django.db import migrations


class Migration(migrations.Migration):
    """Repara bases locales creadas antes de fijar los db_table en 0001_initial.
    No-op en bases nuevas, donde las tablas ya nacen con el nombre correcto."""

    dependencies = [
        ("audit_app", "0002_append_only_and_review_history"),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS audit_app_auditlog RENAME TO audit_log;",
            reverse_sql="ALTER TABLE IF EXISTS audit_log RENAME TO audit_app_auditlog;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE IF EXISTS audit_app_auditreview RENAME TO audit_reviews;",
            reverse_sql="ALTER TABLE IF EXISTS audit_reviews RENAME TO audit_app_auditreview;",
        ),
    ]
