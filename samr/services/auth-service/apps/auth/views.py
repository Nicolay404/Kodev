from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.publisher import publicar_evento

from .models import User
from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RefreshTokenSerializer,
    UserSerializer,
)
from .services import TokenError, generar_jwt_pair, generar_password_reset_token, verify_jwt, verify_password_reset_token


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        try:
            user = User.objects.select_for_update().get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        now = timezone.now()
        if user.locked_until and user.locked_until > now:
            return Response(
                {"error": "Cuenta bloqueada temporalmente"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        if user.locked_until:
            user.failed_attempts = 0
            user.locked_until = None

        if not user.check_password(password):
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.locked_until = now + timedelta(minutes=settings.AUTH_LOCK_MINUTES)
                publicar_evento(
                    "auth.account_locked",
                    {"usuario_id": str(user.id), "email": user.email},
                )
            user.save(update_fields=["failed_attempts", "locked_until"])
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.failed_attempts = 0
        user.locked_until = None
        user.save(update_fields=["failed_attempts", "locked_until"])
        tokens = generar_jwt_pair(user)
        publicar_evento(
            "auth.login_success", {"usuario_id": str(user.id), "email": user.email}
        )
        return Response(tokens)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = verify_jwt(serializer.validated_data["refresh_token"])
            if payload.get("type") != "refresh":
                raise TokenError("Tipo de token inválido")
            user = User.objects.get(id=payload["usuario_id"])
        except (TokenError, User.DoesNotExist, ValueError) as exc:
            return Response({"error": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(generar_jwt_pair(user))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data["current_password"]):
            return Response({"current_password": ["Contraseña actual incorrecta."]}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Contraseña actualizada."})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data["email"]).first()
        if user:
            publicar_evento(
                "auth.password_reset_requested",
                {
                    "usuario_id": str(user.id),
                    "email": user.email,
                    "reset_token": generar_password_reset_token(user),
                    "expires_in_seconds": 900,
                },
            )
        return Response(
            {"detail": "Si la cuenta existe, se enviaron instrucciones de recuperación."},
            status=status.HTTP_202_ACCEPTED,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = verify_jwt(serializer.validated_data["token"])
            user = User.objects.get(id=payload.get("usuario_id"))
            verify_password_reset_token(serializer.validated_data["token"], user)
        except (TokenError, User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Token de recuperación inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.failed_attempts = 0
        user.locked_until = None
        user.save(update_fields=["password", "failed_attempts", "locked_until"])
        return Response({"detail": "Contraseña restablecida."})
