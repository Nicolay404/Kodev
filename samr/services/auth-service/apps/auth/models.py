from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('medical', 'Medical'),
        ('admin', 'Admin'),
        ('system_admin', 'System Admin'),
    )
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {'Success' if self.success else 'Failed'} at {self.timestamp}"
