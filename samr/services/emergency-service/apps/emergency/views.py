from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Emergency
from .serializers import EmergencySerializer
from .permissions import JWTAuthentication
from events.publisher import publicar_evento

class EmergencyListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        emergencies = Emergency.objects.all().order_by('-reported_at')[:50]
        serializer = EmergencySerializer(emergencies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmergencySerializer(data=request.data)
        if serializer.is_valid():
            emergency = serializer.save(patient_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmergencyDispatchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, emergency_id):
        user = request.user
        if getattr(user, 'rol', None) not in ['admin', 'medical']:
            return Response({'error': 'Permiso denegado'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            emergency = Emergency.objects.get(id=emergency_id)
        except Emergency.DoesNotExist:
            return Response({'error': 'Emergencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            
        if emergency.status != 'reported':
            return Response({'error': 'La emergencia ya fue despachada o resuelta'}, status=status.HTTP_400_BAD_REQUEST)
            
        emergency.status = 'dispatched'
        emergency.dispatched_at = timezone.now()
        emergency.save()
        
        publicar_evento('emergency.dispatched', {
            'emergency_id': emergency.id,
            'patient_id': emergency.patient_id,
            'location': emergency.location,
            'dispatched_at': emergency.dispatched_at.isoformat()
        })
        
        serializer = EmergencySerializer(emergency)
        return Response(serializer.data, status=status.HTTP_200_OK)
