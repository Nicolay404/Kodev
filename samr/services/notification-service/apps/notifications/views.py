import jwt
from cryptography.hazmat.primitives import serialization
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .inbox import get_inbox


def _principal(request):
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return None
    try:
        with open(settings.JWT_PUBLIC_KEY_PATH, "rb") as key_file:
            key = serialization.load_pem_public_key(key_file.read())
        payload = jwt.decode(
            authorization[7:],
            key,
            algorithms=["RS256"],
            issuer="samr-auth-service",
        )
        if payload.get("type") != "access":
            return None
        return payload
    except (OSError, jwt.InvalidTokenError, ValueError):
        return None


def health(request):
    return JsonResponse({"status": "ok"})


def notification_list(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    principal = _principal(request)
    if not principal:
        return JsonResponse({"error": "Token inválido o no provisto"}, status=401)
    return JsonResponse(get_inbox().list_for(principal["usuario_id"]), safe=False)


@csrf_exempt
def notification_mark_read(request, notification_id):
    if request.method != "PATCH":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    principal = _principal(request)
    if not principal:
        return JsonResponse({"error": "Token inválido o no provisto"}, status=401)
    notification = get_inbox().mark_read(principal["usuario_id"], notification_id)
    if not notification:
        return JsonResponse({"error": "Notificación no encontrada"}, status=404)
    return JsonResponse(notification)
