from django.urls import path
from .views import IoTEventView, AlertView

urlpatterns = [
    path('iot-events/', IoTEventView.as_view(), name='iot_events'),
    path('alerts/', AlertView.as_view(), name='alerts'),
]
