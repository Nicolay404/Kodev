import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        if not password:
            raise ValueError("La contraseña es obligatoria")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ("patient", "Patient"),
        ("professional", "Professional"),
        ("nurse", "Nurse/Paramedic"),
        ("center_admin", "Center Admin"),
        ("system_admin", "System Admin"),
        ("dpd_delegate", "DPD Delegate"),
    )

    password = models.CharField(max_length=255, db_column="password_hash")
    last_login = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="patient")
    failed_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = "email"

    class Meta:
        db_table = "auth_user"

    @property
    def rol(self):
        """Alias de compatibilidad para el claim JWT utilizado por los servicios."""
        return self.role

    def __str__(self):
        return self.email
