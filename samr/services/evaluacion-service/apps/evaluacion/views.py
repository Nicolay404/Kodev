from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from .models import AvailableCenterCache, Evaluacion, Matching
from .permissions import JWTAuthentication, ServiceTokenAuthentication
from .serializers import AvailableCenterSerializer, EvaluacionSerializer, MatchingRequestSerializer, MatchingSerializer
from .services import find_best_center, mvp_matching_score


class RiesgoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, solicitud_id):
        evaluacion = Evaluacion.objects.filter(solicitud_id=solicitud_id).first()
        return Response(EvaluacionSerializer(evaluacion).data) if evaluacion else Response({"error": "Evaluación no encontrada"}, status=404)


class CentrosDisponiblesView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        centers = AvailableCenterCache.objects.filter(disponible=True).order_by("nombre")
        return Response(AvailableCenterSerializer(centers, many=True).data)


class MatchingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, evaluacion_id):
        if request.user.rol not in {"professional", "center_admin", "system_admin"}:
            return Response({"error": "Permiso denegado"}, status=403)
        evaluacion = Evaluacion.objects.filter(id=evaluacion_id).first()
        if not evaluacion: return Response({"error": "Evaluación no encontrada"}, status=404)
        if hasattr(evaluacion, "matching"): return Response({"error": "La evaluación ya tiene matching"}, status=400)
        serializer = MatchingRequestSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        professional_id = request.user.id if request.user.rol == "professional" else serializer.validated_data.get("professional_id")
        if not professional_id: return Response({"professional_id": ["Obligatorio para administradores."]}, status=400)
        center = find_best_center()
        if not center:
            publicar_evento("matching.fallido", {"evaluacion_id": str(evaluacion.id), "reason": "no_available_center"})
            return Response({"error": "No hay centros disponibles"}, status=409)
        matching = Matching.objects.create(evaluacion=evaluacion, professional_id=professional_id, center_id=center.center_id, score=mvp_matching_score())
        publicar_evento("recursos.asignados", {"evaluacion_id": str(evaluacion.id), "matching_id": str(matching.id), "patient_id": str(serializer.validated_data["patient_id"]), "professional_id": str(matching.professional_id), "center_id": str(matching.center_id), "score": str(matching.score)})
        return Response(MatchingSerializer(matching).data, status=201)


class MisCasosView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.rol == "patient":
            return Response([])
        return Response(EvaluacionSerializer(Evaluacion.objects.order_by("-created_at")[:50], many=True).data)
