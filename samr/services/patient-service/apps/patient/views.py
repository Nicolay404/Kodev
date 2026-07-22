from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from .models import Patient
from .permissions import JWTAuthentication, ServiceTokenAuthentication
from .serializers import PatientSerializer, PatientSummarySerializer


class PatientMeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.rol != "patient":
            return Response({"error": "Acceso exclusivo para pacientes"}, status=403)
        try:
            patient = Patient.objects.get(user_id=request.user.id)
        except Patient.DoesNotExist:
            return Response({"error": "Perfil de paciente no encontrado"}, status=404)
        return Response(PatientSerializer(patient).data)

    def patch(self, request):
        if request.user.rol != "patient":
            return Response({"error": "Acceso exclusivo para pacientes"}, status=403)
        patient = Patient.objects.filter(user_id=request.user.id).first()
        creating = patient is None
        serializer = PatientSerializer(patient, data=request.data, partial=not creating)
        serializer.is_valid(raise_exception=True)
        save_fields = {"user_id": request.user.id}
        if creating:
            save_fields["id"] = request.user.id
        patient = serializer.save(**save_fields)
        publicar_evento("patient.profile_updated", {"patient_id": str(patient.id), "user_id": str(request.user.id)})
        return Response(PatientSerializer(patient).data, status=status.HTTP_201_CREATED if creating else status.HTTP_200_OK)


class PatientSummaryView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return Response({"error": "Paciente no encontrado"}, status=404)
        return Response(PatientSummarySerializer(patient).data)
