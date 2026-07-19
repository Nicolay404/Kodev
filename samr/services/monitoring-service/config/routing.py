import os
from django.urls import path
from consumers.monitoring_consumer import MonitoringConsumer

websocket_urlpatterns = [
    path('ws/monitoring/<int:patient_id>/', MonitoringConsumer.as_asgi()),
]
