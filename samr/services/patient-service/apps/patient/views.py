from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Patient
from .serializers import PatientSerializer, PatientSummarySerializer
from .permissions import JWTAuthentication, ServiceTokenAuthentication
from events.publisher import publicar_evento

class PatientMeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            patient = Patient.objects.get(user_id=request.user.id)
            serializer = PatientSerializer(patient)
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response({'error': 'Perfil de paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        try:
            patient = Patient.objects.get(user_id=request.user.id)
            serializer = PatientSerializer(patient, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                publicar_evento('patient.profile_updated', {'patient_id': patient.id, 'user_id': request.user.id})
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Patient.DoesNotExist:
            # Si no existe, lo creamos
            serializer = PatientSerializer(data=request.data)
            if serializer.is_valid():
                patient = serializer.save(user_id=request.user.id)
                publicar_evento('patient.profile_updated', {'patient_id': patient.id, 'user_id': request.user.id})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientSummaryView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.get(pk=pk)
            serializer = PatientSummarySerializer(patient)
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
