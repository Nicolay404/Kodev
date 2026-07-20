import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("id", "email", "password", "role", "created_at")
        read_only_fields = ("id", "role", "created_at")

    def validate_password(self, value):
        if len(value) < 8 or not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres, letras y números."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
