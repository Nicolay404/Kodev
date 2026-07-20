from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Historial, Consentimiento
from .serializers import HistorialSerializer
from .permissions import JWTAuthentication

class HistorialView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        user = request.user
        # Validar permisos: un paciente solo puede ver su propio historial. Admin/Medical pueden ver cualquiera.
        if user.rol == 'patient' and user.id != patient_id:
            return Response({'error': 'Acceso denegado'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            historial = Historial.objects.get(patient_id=patient_id)
            serializer = HistorialSerializer(historial)
            return Response(serializer.data)
        except Historial.DoesNotExist:
            return Response({'error': 'Historial no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class FHIRHistoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        # Requiere consentimiento activo para exponer en FHIR (RNF-32, RNF-34)
        try:
            consent = Consentimiento.objects.get(patient_id=patient_id)
            if not consent.fhir_enabled:
                return Response({'error': 'El paciente no ha dado su consentimiento para interoperabilidad FHIR'}, status=status.HTTP_403_FORBIDDEN)
        except Consentimiento.DoesNotExist:
            return Response({'error': 'Consentimiento no registrado'}, status=status.HTTP_403_FORBIDDEN)

        try:
            historial = Historial.objects.get(patient_id=patient_id)
        except Historial.DoesNotExist:
            return Response({'error': 'Historial no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Simular transformación básica a FHIR R4
        fhir_bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": []
        }
        
        for entry in historial.data:
            fhir_bundle['entry'].append({
                "resourceType": "Encounter",
                "status": "finished",
                "subject": {"reference": f"Patient/{patient_id}"},
                "period": {"end": entry.get('closed_at')}
            })
            
        return Response(fhir_bundle)
