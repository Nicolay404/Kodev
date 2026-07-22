from django.utils import timezone
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AuditLog, AuditReview
from .permissions import JWTAuthentication
from .serializers import AuditLogSerializer, AuditReviewSerializer, ReviewRequestSerializer


class IsDPDDelegate(BasePermission):
    def has_permission(self, request, view): return bool(request.user and request.user.is_authenticated and request.user.rol == "dpd_delegate")


class AuditDecisionsView(APIView):
    authentication_classes = [JWTAuthentication]; permission_classes = [IsAuthenticated, IsDPDDelegate]
    def get(self, request):
        query = AuditLog.objects.order_by("-id")
        if request.query_params.get("event_type"):
            query = query.filter(event_type=request.query_params["event_type"])
        if request.query_params.get("actor_id"):
            query = query.filter(actor_id=request.query_params["actor_id"])
        if request.query_params.get("created_from"):
            query = query.filter(created_at__gte=request.query_params["created_from"])
        if request.query_params.get("created_to"):
            query = query.filter(created_at__lte=request.query_params["created_to"])
        try:
            limit = min(max(int(request.query_params.get("limit", 100)), 1), 100)
            offset = max(int(request.query_params.get("offset", 0)), 0)
        except ValueError:
            return Response({"error": "limit y offset deben ser enteros"}, status=400)
        return Response(AuditLogSerializer(query[offset:offset + limit], many=True).data)


class AuditDecisionReviewView(APIView):
    authentication_classes = [JWTAuthentication]; permission_classes = [IsAuthenticated, IsDPDDelegate]
    def patch(self, request, audit_log_id):
        if not AuditLog.objects.filter(id=audit_log_id).exists(): return Response({"error": "Registro no encontrado"}, status=404)
        serializer = ReviewRequestSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        review = AuditReview.objects.create(audit_log_id=audit_log_id, **serializer.validated_data, revisado_por=request.user.id, fecha_revision=timezone.now())
        return Response(AuditReviewSerializer(review).data)
