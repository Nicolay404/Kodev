from datetime import timedelta

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from apps.auth.management.commands.reset_demo_passwords import DEMO_USERS
from apps.auth.models import User


@pytest.mark.django_db
def test_reset_demo_passwords_updates_only_expected_accounts():
    for email, role in DEMO_USERS.items():
        User.objects.create_user(
            email=email,
            password="Previous123",
            role="pacient" if email == "user@prueba1.com" else role,
            failed_attempts=5,
            locked_until=timezone.now() + timedelta(minutes=10),
        )

    call_command("reset_demo_passwords", password="Changed123")

    for email, role in DEMO_USERS.items():
        user = User.objects.get(email=email)
        assert user.role == role
        assert user.check_password("Changed123")
        assert user.failed_attempts == 0
        assert user.locked_until is None


@pytest.mark.django_db
def test_reset_demo_passwords_aborts_when_an_account_is_missing():
    email = next(iter(DEMO_USERS))
    user = User.objects.create_user(
        email=email,
        password="Previous123",
        role=DEMO_USERS[email],
    )

    with pytest.raises(CommandError, match="No se modificó ninguna cuenta"):
        call_command("reset_demo_passwords", password="Changed123")

    user.refresh_from_db()
    assert user.check_password("Previous123")
