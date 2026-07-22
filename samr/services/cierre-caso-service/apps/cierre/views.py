from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from .models import Caso
from .permissions import JWTAuthentication
from .serializers import CasoSerializer, CloseCaseSerializer
from .services import calculate_integrity_hash, verify_case


class CierreCasoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, caso_id):
        if request.user.rol != "professional": return Response({"error": "Solo un profesional puede cerrar casos"}, status=403)
        case = Caso.objects.filter(id=caso_id).first()
        if not case: return Response({"error": "Caso no encontrado"}, status=404)
        if case.status == "closed": return Response({"error": "Caso ya cerrado"}, status=400)
        serializer = CloseCaseSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        case.clinical_notes = serializer.validated_data["clinical_notes"]
        readiness = verify_case(case)
        if not readiness["ready_to_close"]: return Response({"error": "El caso no tiene una fuente de atención íntegra", "verification": readiness}, status=409)
        case.integrity_hash = calculate_integrity_hash(case); case.status = "closed"; case.closed_at = timezone.now()
        case.save(update_fields=["clinical_notes", "integrity_hash", "status", "closed_at"])
        publicar_evento("caso.cerrado", {"caso_id": str(case.id), "patient_id": str(case.patient_id), "teleconsult_id": str(case.teleconsult_id) if case.teleconsult_id else None, "emergency_id": str(case.emergency_id) if case.emergency_id else None, "clinical_notes": case.clinical_notes, "integrity_hash": case.integrity_hash, "closed_at": case.closed_at.isoformat()})
        return Response(CasoSerializer(case).data)


class VerificarCasoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, caso_id):
        if request.user.rol not in {"professional", "center_admin"}: return Response({"error": "Permiso denegado"}, status=403)
        case = Caso.objects.filter(id=caso_id).first()
        return Response({"error": "Caso no encontrado"}, status=404) if not case else Response({"caso_id": str(case.id), "status": case.status, **verify_case(case)})


class MisCasosView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        rol = request.user.rol
        if rol == "patient":
            cases = Caso.objects.filter(patient_id=request.user.id).order_by("-closed_at")
        elif rol in {"professional", "center_admin"}:
            cases = Caso.objects.order_by("-closed_at")
        else:
            return Response({"error": "Permiso denegado"}, status=403)
        return Response(CasoSerializer(cases[:50], many=True).data)
