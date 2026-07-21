from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Verifica la conectividad del servicio con su base PostgreSQL."
    requires_system_checks = []

    def handle(self, *args, **options):
        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                if cursor.fetchone() != (1,):
                    raise RuntimeError("PostgreSQL no devolvió el valor esperado")
        except Exception as exc:
            raise CommandError(f"health check fallido: {exc}") from exc
        self.stdout.write("ok")
