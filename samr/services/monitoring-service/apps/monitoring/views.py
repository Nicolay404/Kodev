from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from .models import Alert, VitalSign
from .permissions import DeviceTokenAuthentication, JWTAuthentication
from .serializers import AlertSerializer, VitalSignSerializer
from .services import cache_reading, detect_anomalies, is_device_registered


class IoTEventView(APIView):
    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VitalSignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not is_device_registered(data["device_id"], data["patient_id"]):
            return Response({"error": "Dispositivo no registrado para el paciente"}, status=403)
        reading = serializer.save()
        cache_reading(reading)
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(f"monitoring_{reading.patient_id}", {"type": "vital_update", "data": VitalSignSerializer(reading).data})
        anomalies = detect_anomalies(reading.value)
        if anomalies:
            alert = Alert.objects.create(patient_id=reading.patient_id, severity="critical")
            payload = {"patient_id": str(reading.patient_id), "device_id": str(reading.device_id), "anomalies": anomalies, "value": reading.value, "alert_id": str(alert.id)}
            publicar_evento("vitals.critical_detected", payload)
            async_to_sync(layer.group_send)(f"monitoring_{reading.patient_id}", {"type": "alert_triggered", "data": payload})
        return Response(VitalSignSerializer(reading).data, status=201)


class AlertView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.rol == "patient":
            alerts = Alert.objects.filter(patient_id=request.user.id)
        elif request.user.rol in {"professional", "nurse", "center_admin", "system_admin"}:
            alerts = Alert.objects.all()
        else:
            return Response({"error": "Permiso denegado"}, status=403)
        return Response(AlertSerializer(alerts.order_by("-created_at")[:50], many=True).data)


class VitalSignView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        readings = VitalSign.objects.all()
        if request.user.rol == "patient":
            readings = readings.filter(patient_id=request.user.id)
        elif request.user.rol in {"professional", "nurse", "center_admin", "system_admin"}:
            patient_id = request.query_params.get("patient_id")
            if patient_id:
                readings = readings.filter(patient_id=patient_id)
        else:
            return Response({"error": "Permiso denegado"}, status=403)
        return Response(VitalSignSerializer(readings.order_by("-recorded_at")[:100], many=True).data)
