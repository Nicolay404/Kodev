from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import IoTReading, Alert
from .serializers import IoTReadingSerializer, AlertSerializer
from .permissions import JWTAuthentication, DeviceTokenAuthentication
from .services import detect_anomalies
from events.publisher import publicar_evento
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class IoTEventView(APIView):
    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IoTReadingSerializer(data=request.data)
        if serializer.is_valid():
            reading = serializer.save()
            
            # Notificar vía WebSocket al frontend en tiempo real
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"monitoring_{reading.patient_id}",
                {
                    "type": "vital_update",
                    "data": serializer.data
                }
            )
            
            # Detectar anomalías
            anomalies = detect_anomalies(reading.vitals)
            if anomalies:
                for anomaly in anomalies:
                    Alert.objects.create(
                        patient_id=reading.patient_id,
                        tipo=anomaly,
                        detectada_anomalia=True
                    )
                    
                    # Publicar evento crítico
                    publicar_evento('vitals.critical_detected', {
                        'patient_id': reading.patient_id,
                        'device_id': reading.device_id,
                        'anomaly_type': anomaly,
                        'vitals': reading.vitals
                    })
                    
                    # También notificar alerta por WS
                    async_to_sync(channel_layer.group_send)(
                        f"monitoring_{reading.patient_id}",
                        {
                            "type": "alert_triggered",
                            "data": {
                                "patient_id": reading.patient_id,
                                "anomaly_type": anomaly
                            }
                        }
                    )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AlertView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # En la vida real, se filtrarían por médico responsable o centro.
        alerts = Alert.objects.all().order_by('-created_at')[:50]
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)
