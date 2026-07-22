from django.urls import path
from .views import AlertView, IoTEventView, VitalSignView

urlpatterns = [
    path('iot-events/', IoTEventView.as_view(), name='iot_events'),
    path('alerts/', AlertView.as_view(), name='alerts'),
    path('vital-signs/', VitalSignView.as_view(), name='vital_signs'),
]
