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
    def get(self, request): return Response(AuditLogSerializer(AuditLog.objects.order_by("-id")[:100], many=True).data)


class AuditDecisionReviewView(APIView):
    authentication_classes = [JWTAuthentication]; permission_classes = [IsAuthenticated, IsDPDDelegate]
    def patch(self, request, audit_log_id):
        if not AuditLog.objects.filter(id=audit_log_id).exists(): return Response({"error": "Registro no encontrado"}, status=404)
        serializer = ReviewRequestSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        review, _ = AuditReview.objects.update_or_create(audit_log_id=audit_log_id, defaults={**serializer.validated_data, "revisado_por": request.user.id, "fecha_revision": timezone.now()})
        return Response(AuditReviewSerializer(review).data)
