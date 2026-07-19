from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Evaluacion, Matching
from .serializers import EvaluacionSerializer, MatchingSerializer
from .permissions import JWTAuthentication, ServiceTokenAuthentication
from .services import find_best_center
from events.publisher import publicar_evento

class RiesgoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, solicitud_id):
        try:
            evaluacion = Evaluacion.objects.get(solicitud_id=solicitud_id)
            serializer = EvaluacionSerializer(evaluacion)
            return Response(serializer.data)
        except Evaluacion.DoesNotExist:
            return Response({'error': 'Evaluación no encontrada'}, status=status.HTTP_404_NOT_FOUND)

class CentrosDisponiblesView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # En la realidad esto leería de una caché Redis o DB sincronizada.
        centros = [
            {'id': 1, 'name': 'Hospital General', 'available_beds': 5},
            {'id': 2, 'name': 'Clínica San José', 'available_beds': 2},
        ]
        return Response(centros)

class MatchingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, evaluacion_id):
        try:
            evaluacion = Evaluacion.objects.get(id=evaluacion_id)
        except Evaluacion.DoesNotExist:
            return Response({'error': 'Evaluación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            
        if hasattr(evaluacion, 'matching'):
            return Response({'error': 'Esta evaluación ya tiene un matching'}, status=status.HTTP_400_BAD_REQUEST)
            
        best_center = find_best_center(evaluacion.id)
        
        matching = Matching.objects.create(
            evaluacion=evaluacion,
            centro_asignado=best_center['centro_asignado'],
            recursos=best_center['recursos']
        )
        
        publicar_evento('recursos.asignados', {
            'evaluacion_id': evaluacion.id,
            'matching_id': matching.id,
            'centro_asignado': matching.centro_asignado
        })
        
        serializer = MatchingSerializer(matching)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
