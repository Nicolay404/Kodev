from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, LoginSerializer, RefreshTokenSerializer
from .models import User, LoginAttempt
from .services import generar_jwt_pair, verify_jwt
from django.utils import timezone
import datetime
from events.publisher import publicar_evento

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def check_lock(self, user):
        ten_mins_ago = timezone.now() - datetime.timedelta(minutes=10)
        failed_attempts = LoginAttempt.objects.filter(
            user=user, 
            success=False, 
            timestamp__gte=ten_mins_ago
        ).count()
        return failed_attempts >= 5

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if self.check_lock(user):
            publicar_evento('auth.account_locked', {'usuario_id': user.id, 'email': user.email})
            return Response({'error': 'Cuenta bloqueada temporalmente'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
        if user.check_password(password):
            LoginAttempt.objects.create(user=user, success=True)
            tokens = generar_jwt_pair(user)
            publicar_evento('auth.login_success', {'usuario_id': user.id, 'email': user.email})
            return Response(tokens, status=status.HTTP_200_OK)
        else:
            LoginAttempt.objects.create(user=user, success=False)
            if self.check_lock(user):
                publicar_evento('auth.account_locked', {'usuario_id': user.id, 'email': user.email})
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        token = serializer.validated_data['refresh_token']
        try:
            payload = verify_jwt(token)
            if payload.get('type') != 'refresh':
                return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
                
            user = User.objects.get(id=payload['usuario_id'])
            tokens = generar_jwt_pair(user)
            return Response(tokens, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
