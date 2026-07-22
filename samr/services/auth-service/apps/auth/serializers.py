import re
from django.utils import timezone

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User

# Versión vigente de los Términos y Condiciones / Tratamiento de Datos (LOPDP Ecuador)
# que el usuario acepta al registrarse. Súbela cuando el texto legal cambie de forma
# sustancial, para poder auditar con qué versión aceptó cada usuario.
TERMS_VERSION = "1.0"


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    terms_accepted = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "role", "created_at", "terms_accepted")
        read_only_fields = ("id", "role", "created_at")

    def validate_password(self, value):
        if len(value) < 8 or not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres, letras y números."
            )
        return value

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                "Debes aceptar los Términos y Condiciones y el Tratamiento de Datos para registrarte."
            )
        return value

    def create(self, validated_data):
        validated_data.pop("terms_accepted")
        return User.objects.create_user(
            terms_accepted_at=timezone.now(),
            terms_version=TERMS_VERSION,
            **validated_data,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(trim_whitespace=False)
    new_password = serializers.CharField(trim_whitespace=False)

    def validate_new_password(self, value):
        validate_password(value)
        if len(value) < 8 or not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres, letras y números."
            )
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(trim_whitespace=False)

    def validate_new_password(self, value):
        return PasswordChangeSerializer().validate_new_password(value)
