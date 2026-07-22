from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.auth.models import User


DEMO_USERS = {
    "delegado.dpd@samr-salud.gob.ec": "dpd_delegate",
    "user@prueba1.com": "patient",
    "paciente.juan@gmail.com": "patient",
    "paciente.maria@gmail.com": "patient",
    "dr.mendoza@samr-salud.gob.ec": "professional",
    "enf.torres@samr-salud.gob.ec": "nurse",
    "admin.centro@samr-salud.gob.ec": "center_admin",
    "admin.sistema@samr-salud.gob.ec": "system_admin",
}


class Command(BaseCommand):
    help = (
        "Crea (si no existen) y restablece la contraseña de las cuentas demo del "
        "MVP, una por cada rol, para pruebas locales."
    )

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

        created, updated = 0, 0
        with transaction.atomic():
            existing = {
                user.email: user
                for user in User.objects.select_for_update().filter(
                    email__in=DEMO_USERS
                )
            }
            for email, role in DEMO_USERS.items():
                user = existing.get(email)
                if user is None:
                    user = User(email=email, role=role)
                    created += 1
                else:
                    user.role = role
                    updated += 1
                user.set_password(password)
                user.failed_attempts = 0
                user.locked_until = None
                user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Cuentas demo listas: {created} creadas, {updated} restablecidas "
                f"(total {len(DEMO_USERS)})."
            )
        )
