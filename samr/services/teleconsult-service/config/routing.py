import os
from django.urls import path
from consumers.webrtc_consumer import WebRTCConsumer

websocket_urlpatterns = [
    path('ws/teleconsult/<str:room_token>/', WebRTCConsumer.as_asgi()),
]
