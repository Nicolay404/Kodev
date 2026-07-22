from django.db import migrations, models


def create_append_only_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        CREATE OR REPLACE FUNCTION samr_prevent_audit_log_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only';
        END;
        $$ LANGUAGE plpgsql;
        DROP TRIGGER IF EXISTS audit_log_append_only ON audit_app_auditlog;
        CREATE TRIGGER audit_log_append_only
        BEFORE UPDATE OR DELETE ON audit_app_auditlog
        FOR EACH ROW EXECUTE FUNCTION samr_prevent_audit_log_mutation();
        """
    )


def drop_append_only_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("DROP TRIGGER IF EXISTS audit_log_append_only ON audit_app_auditlog;")
    schema_editor.execute("DROP FUNCTION IF EXISTS samr_prevent_audit_log_mutation();")


class Migration(migrations.Migration):
    dependencies = [("audit_app", "0001_initial")]
    operations = [
        migrations.AlterField(
            model_name="auditreview",
            name="audit_log_id",
            field=models.BigIntegerField(),
        ),
        migrations.RunPython(create_append_only_trigger, drop_append_only_trigger),
    ]
