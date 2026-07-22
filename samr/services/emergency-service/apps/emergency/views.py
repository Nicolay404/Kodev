from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from .models import Emergency, FirstAidGuide
from .permissions import JWTAuthentication
from .serializers import EmergencySerializer


def create_emergency(patient_id, triage_level):
    emergency = Emergency.objects.create(patient_id=patient_id, triage_level=triage_level)
    FirstAidGuide.objects.create(emergency=emergency, contenido=settings.MVP_FIRST_AID_GUIDE)
    payload = {"emergency_id": str(emergency.id), "patient_id": str(emergency.patient_id), "triage_level": emergency.triage_level}
    publicar_evento("emergency.created", payload)
    publicar_evento("ai.decision_logged", {"decision_type": "first_aid_guide", "actor_id": None, "payload": payload, "ai_confidence": None, "ai_explainability": {"adapter": "mvp_static_guide", "clinical_validation": False}})
    return emergency


class EmergencyListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = Emergency.objects.order_by("-created_at")
        if request.user.rol == "patient": query = query.filter(patient_id=request.user.id)
        elif request.user.rol not in {"professional", "nurse", "center_admin"}: return Response({"error": "Permiso denegado"}, status=403)
        return Response(EmergencySerializer(query[:50], many=True).data)
    def post(self, request):
        if request.user.rol != "patient": return Response({"error": "Solo el paciente puede reportar su emergencia"}, status=403)
        triage = request.data.get("triage_level")
        if not triage: return Response({"triage_level": ["Este campo es obligatorio."]}, status=400)
        return Response(EmergencySerializer(create_emergency(request.user.id, triage)).data, status=201)


class EmergencyDispatchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, emergency_id):
        if request.user.rol not in {"professional", "nurse", "center_admin"}: return Response({"error": "Permiso denegado"}, status=403)
        emergency = Emergency.objects.filter(id=emergency_id).first()
        if not emergency: return Response({"error": "Emergencia no encontrada"}, status=404)
        if emergency.status != "pending": return Response({"error": "La emergencia no está pendiente"}, status=400)
        emergency.status = "dispatched"; emergency.save(update_fields=["status"])
        publicar_evento("emergency.dispatched", {"emergency_id": str(emergency.id), "patient_id": str(emergency.patient_id), "triage_level": emergency.triage_level})
        return Response(EmergencySerializer(emergency).data)


class EmergencyDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, emergency_id):
        emergency = Emergency.objects.filter(id=emergency_id).first()
        if not emergency:
            return Response({"error": "Emergencia no encontrada"}, status=404)
        if request.user.rol == "patient" and str(emergency.patient_id) != str(request.user.id):
            return Response({"error": "Permiso denegado"}, status=403)
        if request.user.rol not in {"patient", "professional", "nurse", "center_admin"}:
            return Response({"error": "Permiso denegado"}, status=403)
        return Response(EmergencySerializer(emergency).data)
