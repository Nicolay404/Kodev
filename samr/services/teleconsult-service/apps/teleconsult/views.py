from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from .models import TeleconsultSession
from .permissions import JWTAuthentication
from .serializers import TeleconsultCreateSerializer, TeleconsultSessionSerializer


def publish_started(session):
    publicar_evento("teleconsult.session_started", {"session_id": str(session.id), "room_token": session.room_token, "patient_id": str(session.patient_id), "professional_id": str(session.professional_id), "emergency_id": str(session.emergency_id) if session.emergency_id else None})


class TeleconsultSessionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.user.rol not in {"professional", "center_admin", "system_admin"}:
            return Response({"error": "Permiso denegado"}, status=403)
        serializer = TeleconsultCreateSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        professional_id = request.user.id if request.user.rol == "professional" else serializer.validated_data.get("professional_id")
        if not professional_id: return Response({"professional_id": ["Obligatorio para administradores."]}, status=400)
        session = TeleconsultSession.objects.create(patient_id=serializer.validated_data["patient_id"], professional_id=professional_id, emergency_id=serializer.validated_data.get("emergency_id"))
        publish_started(session)
        return Response(TeleconsultSessionSerializer(session).data, status=201)
