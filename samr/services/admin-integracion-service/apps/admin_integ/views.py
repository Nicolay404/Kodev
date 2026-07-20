from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from tasks.validate_center import validate_center_m2m
from .models import Center, Device
from .permissions import DualAuthentication, IsServiceOrAdmin, IsSystemAdmin
from .serializers import CenterRegisterSerializer, CenterSerializer, DeviceRegisterSerializer, DeviceSerializer


class CenterRegisterView(APIView):
    authentication_classes = [DualAuthentication]; permission_classes = [IsSystemAdmin]
    def post(self, request):
        serializer = CenterRegisterSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        external = {key: serializer.validated_data[key] for key in ("license_number", "specialties")}
        center = Center.objects.create(**{key: value for key, value in serializer.validated_data.items() if key not in external})
        publicar_evento("center.registration_requested", {"center_id": str(center.id), "license_number": external["license_number"], "specialties": external["specialties"], "geo": {"latitude": str(center.latitude), "longitude": str(center.longitude)}})
        validate_center_m2m.delay(str(center.id))
        return Response(CenterSerializer(center).data, status=201)


class AvailableCentersView(APIView):
    authentication_classes = [DualAuthentication]; permission_classes = [IsServiceOrAdmin]
    def get(self, request): return Response(CenterSerializer(Center.objects.filter(status="validated"), many=True).data)


class DeviceRegisterView(APIView):
    authentication_classes = [DualAuthentication]; permission_classes = [IsSystemAdmin]
    def post(self, request):
        serializer = DeviceRegisterSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        device = Device.objects.create(patient_id=serializer.validated_data["patient_id"], device_type=serializer.validated_data["device_type"], registered_by=request.user.id)
        publicar_evento("device.registered", {"device_id": str(device.id), "patient_id": str(device.patient_id), "device_type": device.device_type, "serial_number": serializer.validated_data["serial_number"]})
        return Response(DeviceSerializer(device).data, status=201)
