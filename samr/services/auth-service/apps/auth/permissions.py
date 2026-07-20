from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from .services import verify_jwt
from .models import User

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate_header(self, request):
        return 'Bearer'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        
        try:
            payload = verify_jwt(token)
            if payload.get('type') != 'access':
                raise AuthenticationFailed('Tipo de token inválido. Se requiere un access token.')
                
            user = User.objects.get(id=payload['usuario_id'])
            return (user, token)
        except User.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado.')
        except Exception as e:
            raise AuthenticationFailed(f'Token inválido: {str(e)}')
