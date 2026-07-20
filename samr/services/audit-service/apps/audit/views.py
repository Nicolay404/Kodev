from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import DecisionIA
from .serializers import DecisionIASerializer
from .permissions import JWTAuthentication

class IsDPDDelegate(IsAuthenticated):
    """
    Permiso personalizado para restringir el acceso únicamente a delegados DPD.
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return getattr(request.user, 'rol', None) == 'dpd_delegate'

class AuditDecisionsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsDPDDelegate]

    def get(self, request):
        # Opcional: paginación o filtros (RF-20, RNF-38)
        decisions = DecisionIA.objects.all().order_by('-created_at')[:100]
        serializer = DecisionIASerializer(decisions, many=True)
        return Response(serializer.data)

class AuditDecisionReviewView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsDPDDelegate]

    def patch(self, request, audit_log_id):
        try:
            log = DecisionIA.objects.get(id=audit_log_id)
        except DecisionIA.DoesNotExist:
            return Response({'error': 'Registro de auditoría no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
        notes = request.data.get('review_notes')
        if notes:
            log.review_notes = notes
            log.reviewed = True
            log.reviewed_at = timezone.now()
            log.reviewed_by = request.user.id
            log.save()
            
            serializer = DecisionIASerializer(log)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return Response({'error': 'Se requieren notas de revisión (review_notes)'}, status=status.HTTP_400_BAD_REQUEST)
