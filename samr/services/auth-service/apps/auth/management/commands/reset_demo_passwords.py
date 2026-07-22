from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.auth.models import User


DEMO_USERS = {
    "delegado.dpd@samr-salud.gob.ec": "dpd_delegate",
    "user@prueba1.com": "patient",
    "paciente.juan@gmail.com": "patient",
    "paciente.maria@gmail.com": "patient",
    "dr.mendoza@samr-salud.gob.ec": "professional",
    "admin.sistema@samr-salud.gob.ec": "system_admin",
}


class Command(BaseCommand):
    help = "Restablece las cuentas demo existentes sin crear usuarios nuevos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            required=True,
            help="Contraseña temporal común para las cuentas demo del MVP.",
        )

    def handle(self, *args, **options):
        password = options["password"]
        if (
            len(password) < 8
            or not any(character.isalpha() for character in password)
            or not any(character.isdigit() for character in password)
        ):
            raise CommandError(
                "La contraseña debe tener al menos 8 caracteres, una letra y un número."
            )

        with transaction.atomic():
            users = {
                user.email: user
                for user in User.objects.select_for_update().filter(
                    email__in=DEMO_USERS
                )
            }
            missing_users = sorted(set(DEMO_USERS) - set(users))
            if missing_users:
                raise CommandError(
                    "No se modificó ninguna cuenta. Faltan usuarios demo: "
                    + ", ".join(missing_users)
                )

            for email, role in DEMO_USERS.items():
                user = users[email]
                user.role = role
                user.set_password(password)
                user.failed_attempts = 0
                user.locked_until = None
                user.save(
                    update_fields=(
                        "role",
                        "password",
                        "failed_attempts",
                        "locked_until",
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Se restablecieron {len(DEMO_USERS)} cuentas demo existentes."
            )
        )
