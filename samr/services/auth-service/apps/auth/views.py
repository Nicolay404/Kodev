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
from .serializers import LoginSerializer, RefreshTokenSerializer, UserSerializer
from .services import TokenError, generar_jwt_pair, verify_jwt


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
        user.save(update_fields=["failed_attempts", "locked_until", "last_login"])
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
