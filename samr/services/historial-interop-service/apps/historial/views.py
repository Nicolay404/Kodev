from requests import RequestException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Historial
from .permissions import JWTAuthentication
from .serializers import HistorialSerializer
from .services import compose_fhir_bundle, verify_sharing_consent


def can_read(user, patient_id):
    return (user.rol == "patient" and str(user.id) == str(patient_id)) or user.rol in {"professional", "nurse", "center_admin", "system_admin"}


class HistorialView(APIView):
    authentication_classes = [JWTAuthentication]; permission_classes = [IsAuthenticated]
    def get(self, request, patient_id):
        if not can_read(request.user, patient_id): return Response({"error": "Acceso denegado"}, status=403)
        history = Historial.objects.filter(patient_id=patient_id).first()
        return Response(HistorialSerializer(history).data) if history else Response({"error": "Historial no encontrado"}, status=404)


class FHIRHistoryView(APIView):
    authentication_classes = [JWTAuthentication]; permission_classes = [IsAuthenticated]
    def get(self, request, patient_id):
        if not can_read(request.user, patient_id): return Response({"error": "Acceso denegado"}, status=403)
        try:
            if not verify_sharing_consent(patient_id): return Response({"error": "Consentimiento de interoperabilidad no otorgado"}, status=403)
        except RequestException: return Response({"error": "No fue posible verificar el consentimiento"}, status=503)
        history = Historial.objects.filter(patient_id=patient_id).first()
        return Response(compose_fhir_bundle(history), content_type="application/fhir+json") if history else Response({"error": "Historial no encontrado"}, status=404)
