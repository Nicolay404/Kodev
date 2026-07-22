import uuid

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from requests import RequestException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Historial
from .permissions import JWTAuthentication
from .serializers import ClinicalNoteSerializer, HistorialSerializer
from .services import compose_fhir_bundle, verify_sharing_consent


def can_read(user, patient_id):
    return (user.rol == "patient" and str(user.id) == str(patient_id)) or user.rol in {"professional", "nurse", "center_admin", "system_admin"}


class HistorialView(APIView):
    authentication_classes = [JWTAuthentication]; permission_classes = [IsAuthenticated]
    def get(self, request, patient_id):
        if not can_read(request.user, patient_id): return Response({"error": "Acceso denegado"}, status=403)
        history = Historial.objects.filter(patient_id=patient_id).first()
        return Response(HistorialSerializer(history).data) if history else Response({"error": "Historial no encontrado"}, status=404)

    @transaction.atomic
    def post(self, request, patient_id):
        if request.user.rol not in {"professional", "nurse"}:
            return Response({"error": "Solo el personal clínico puede agregar notas"}, status=403)
        serializer = ClinicalNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        history, _ = Historial.objects.select_for_update().get_or_create(patient_id=patient_id)
        history.eventos.append(
            {
                "event_type": "clinical.note",
                "event_key": f"clinical.note:{uuid.uuid4()}",
                "note": serializer.validated_data["note"],
                "author_id": str(request.user.id),
                "created_at": timezone.now().isoformat(),
            }
        )
        history.save(update_fields=["eventos", "updated_at"])
        cache.delete(f"fhir:{patient_id}")
        return Response(HistorialSerializer(history).data, status=201)


class FHIRHistoryView(APIView):
    authentication_classes = [JWTAuthentication]; permission_classes = [IsAuthenticated]
    def get(self, request, patient_id):
        if not can_read(request.user, patient_id): return Response({"error": "Acceso denegado"}, status=403)
        try:
            if not verify_sharing_consent(patient_id): return Response({"error": "Consentimiento de interoperabilidad no otorgado"}, status=403)
        except RequestException: return Response({"error": "No fue posible verificar el consentimiento"}, status=503)
        history = Historial.objects.filter(patient_id=patient_id).first()
        return Response(compose_fhir_bundle(history), content_type="application/fhir+json") if history else Response({"error": "Historial no encontrado"}, status=404)
