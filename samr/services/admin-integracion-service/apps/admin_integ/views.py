from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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


class CenterListView(APIView):
    authentication_classes = [DualAuthentication]
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        status_filter = request.query_params.get("status")
        centers = Center.objects.all()
        if status_filter:
            centers = centers.filter(status=status_filter)
        return Response(CenterSerializer(centers.order_by("name"), many=True).data)


class CenterDetailView(APIView):
    authentication_classes = [DualAuthentication]
    permission_classes = [IsSystemAdmin]

    def get(self, request, center_id):
        center = Center.objects.filter(id=center_id).first()
        return Response(CenterSerializer(center).data) if center else Response({"error": "Centro no encontrado"}, status=404)


class DeviceListView(APIView):
    authentication_classes = [DualAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.rol == "patient":
            devices = Device.objects.filter(patient_id=request.user.id)
        elif request.user.rol == "system_admin":
            devices = Device.objects.all()
            patient_id = request.query_params.get("patient_id")
            if patient_id:
                devices = devices.filter(patient_id=patient_id)
        else:
            return Response({"error": "Permiso denegado"}, status=403)
        return Response(DeviceSerializer(devices.order_by("device_type", "id"), many=True).data)


class DeviceDetailView(APIView):
    authentication_classes = [DualAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, device_id):
        device = Device.objects.filter(id=device_id).first()
        if not device:
            return Response({"error": "Dispositivo no encontrado"}, status=404)
        if request.user.rol == "patient" and str(device.patient_id) != str(request.user.id):
            return Response({"error": "Permiso denegado"}, status=403)
        if request.user.rol not in {"patient", "system_admin"}:
            return Response({"error": "Permiso denegado"}, status=403)
        return Response(DeviceSerializer(device).data)
