from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Caso
from .serializers import CasoSerializer
from .permissions import JWTAuthentication
from events.publisher import publicar_evento

class CierreCasoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, caso_id):
        # Solamente personal médico o admin puede cerrar
        user = request.user
        if getattr(user, 'rol', None) not in ['medical', 'admin']:
            return Response({'error': 'No tiene permisos para cerrar casos'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            caso = Caso.objects.get(id=caso_id)
        except Caso.DoesNotExist:
            return Response({'error': 'Caso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
        if caso.status == 'closed':
            return Response({'error': 'Este caso ya se encuentra cerrado'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Validar integridad: que existan notas si es requerido (RNF-28)
        notes = request.data.get('notes', '')
        if not notes and not caso.notes:
            return Response({'error': 'Las notas de cierre son obligatorias'}, status=status.HTTP_400_BAD_REQUEST)
            
        if notes:
            caso.notes = notes
            
        caso.status = 'closed'
        caso.closed_at = timezone.now()
        caso.save()
        
        # Publicar evento para M4 (historial-interop-service)
        publicar_evento('caso.cerrado', {
            'caso_id': caso.id,
            'patient_id': caso.patient_id,
            'closed_at': caso.closed_at.isoformat(),
            'notes': caso.notes
        })
        
        serializer = CasoSerializer(caso)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VerificarCasoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, caso_id):
        try:
            caso = Caso.objects.get(id=caso_id)
        except Caso.DoesNotExist:
            return Response({'error': 'Caso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
        # Lógica para verificar integridad RNF-28
        ready_to_close = bool(caso.notes)
        return Response({
            'caso_id': caso.id,
            'status': caso.status,
            'ready_to_close': ready_to_close
        })
