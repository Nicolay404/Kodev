from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import TeleconsultSession
from .serializers import TeleconsultSessionSerializer
from .permissions import JWTAuthentication
from events.publisher import publicar_evento

class TeleconsultSessionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # El request debe traer patient_id
        serializer = TeleconsultSessionSerializer(data=request.data)
        if serializer.is_valid():
            # Asignar doctor que crea la sesión si es medical
            user = request.user
            if hasattr(user, 'rol') and user.rol == 'medical':
                serializer.validated_data['doctor_id'] = user.id
                
            session = serializer.save()
            
            publicar_evento('atencion.iniciada', {
                'session_id': session.id,
                'room_token': session.room_token,
                'patient_id': session.patient_id,
                'doctor_id': session.doctor_id
            })
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
