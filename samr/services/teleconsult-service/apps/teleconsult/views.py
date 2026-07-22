from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from .models import TeleconsultSession
from .permissions import JWTAuthentication
from .serializers import TeleconsultCloseSerializer, TeleconsultCreateSerializer, TeleconsultSessionSerializer


def publish_started(session):
    publicar_evento("teleconsult.session_started", {"session_id": str(session.id), "room_token": session.room_token, "patient_id": str(session.patient_id), "professional_id": str(session.professional_id), "emergency_id": str(session.emergency_id) if session.emergency_id else None})


class TeleconsultSessionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = TeleconsultSession.objects.all()
        if request.user.rol == "patient":
            sessions = sessions.filter(patient_id=request.user.id)
        elif request.user.rol == "professional":
            sessions = sessions.filter(professional_id=request.user.id)
        elif request.user.rol not in {"center_admin", "system_admin"}:
            return Response({"error": "Permiso denegado"}, status=403)
        return Response(TeleconsultSessionSerializer(sessions.order_by("-id")[:50], many=True).data)

    def post(self, request):
        if request.user.rol not in {"professional", "center_admin", "system_admin"}:
            return Response({"error": "Permiso denegado"}, status=403)
        serializer = TeleconsultCreateSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        professional_id = request.user.id if request.user.rol == "professional" else serializer.validated_data.get("professional_id")
        if not professional_id: return Response({"professional_id": ["Obligatorio para administradores."]}, status=400)
        session = TeleconsultSession.objects.create(patient_id=serializer.validated_data["patient_id"], professional_id=professional_id, emergency_id=serializer.validated_data.get("emergency_id"))
        publish_started(session)
        return Response(TeleconsultSessionSerializer(session).data, status=201)


class TeleconsultSessionDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_session(self, request, session_id):
        session = TeleconsultSession.objects.filter(id=session_id).first()
        if not session:
            return None, Response({"error": "Teleconsulta no encontrada"}, status=404)
        allowed = (
            (request.user.rol == "patient" and str(session.patient_id) == str(request.user.id))
            or (request.user.rol == "professional" and str(session.professional_id) == str(request.user.id))
            or request.user.rol in {"center_admin", "system_admin"}
        )
        if not allowed:
            return None, Response({"error": "Permiso denegado"}, status=403)
        return session, None

    def get(self, request, session_id):
        session, error = self.get_session(request, session_id)
        return error or Response(TeleconsultSessionSerializer(session).data)


class TeleconsultCloseView(TeleconsultSessionDetailView):
    def post(self, request, session_id):
        session, error = self.get_session(request, session_id)
        if error:
            return error
        if request.user.rol != "professional" or str(session.professional_id) != str(request.user.id):
            return Response({"error": "Solo el profesional asignado puede cerrar la teleconsulta"}, status=403)
        if session.status == "closed":
            return Response({"error": "La teleconsulta ya está cerrada"}, status=409)

        serializer = TeleconsultCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session.diagnosis = serializer.validated_data["diagnosis"]
        session.ai_recommendation = serializer.validated_data.get("ai_recommendation", {})
        session.status = "closed"
        session.closed_at = timezone.now()
        session.save(update_fields=["diagnosis", "ai_recommendation", "status", "closed_at"])
        publicar_evento(
            "teleconsult.closed",
            {
                "session_id": str(session.id),
                "patient_id": str(session.patient_id),
                "professional_id": str(session.professional_id),
                "diagnosis": session.diagnosis,
                "closed_at": session.closed_at.isoformat(),
            },
        )
        return Response(TeleconsultSessionSerializer(session).data)
