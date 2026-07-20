from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Center, Device
from .serializers import CenterSerializer, DeviceSerializer
from .permissions import DualAuthentication, IsSystemAdmin, IsServiceOrAdmin
from events.publisher import publicar_evento

class CenterRegisterView(APIView):
    authentication_classes = [DualAuthentication]
    permission_classes = [IsSystemAdmin]

    def post(self, request):
        serializer = CenterSerializer(data=request.data)
        if serializer.is_valid():
            center = serializer.save()
            publicar_evento('center.registered', {
                'center_id': center.id,
                'name': center.name
            })
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AvailableCentersView(APIView):
    authentication_classes = [DualAuthentication]
    permission_classes = [IsServiceOrAdmin] # M2M (evaluacion-service) o Admin

    def get(self, request):
        # Filtra centros que tienen capacidad
        centers = Center.objects.filter(is_active=True, max_capacity__gt=models.F('current_occupancy'))
        serializer = CenterSerializer(centers, many=True)
        return Response(serializer.data)
        
    def get(self, request):
        # Import local to avoid circular dep if needed, but F is at top usually
        from django.db.models import F
        centers = Center.objects.filter(is_active=True, max_capacity__gt=F('current_occupancy'))
        serializer = CenterSerializer(centers, many=True)
        return Response(serializer.data)

class DeviceRegisterView(APIView):
    authentication_classes = [DualAuthentication]
    permission_classes = [IsSystemAdmin]

    def post(self, request):
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = serializer.save()
            publicar_evento('device.registered', {
                'device_id': device.id,
                'mac_address': device.mac_address,
                'patient_id': device.patient_id
            })
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
