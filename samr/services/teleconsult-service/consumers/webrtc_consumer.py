import json
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import models
from apps.teleconsult.models import TeleconsultSession
from apps.teleconsult.permissions import verify_jwt


class WebRTCConsumer(AsyncWebsocketConsumer):
    SIGNAL_TYPES = {"offer", "answer", "ice-candidate"}

    @database_sync_to_async
    def authorized(self, room_token, user_id):
        return TeleconsultSession.objects.filter(room_token=room_token, status="active").filter(models.Q(patient_id=user_id) | models.Q(professional_id=user_id)).exists()

    async def connect(self):
        self.room_token = self.scope["url_route"]["kwargs"]["room_token"]
        self.room_group_name = f"teleconsult_{self.room_token}"
        token = parse_qs(self.scope["query_string"].decode()).get("token", [None])[0]
        if not token: await self.close(code=4001); return
        try: payload = verify_jwt(token)
        except Exception: await self.close(code=4003); return
        if not await self.authorized(self.room_token, payload.get("usuario_id")):
            await self.close(code=4003); return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name); await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"): await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try: message = json.loads(text_data)
        except json.JSONDecodeError: await self.close(code=4002); return
        if message.get("type") not in self.SIGNAL_TYPES: await self.close(code=4002); return
        await self.channel_layer.group_send(self.room_group_name, {"type": "webrtc_message", "message": message, "sender": self.channel_name})

    async def webrtc_message(self, event):
        if self.channel_name != event["sender"]: await self.send(text_data=json.dumps(event["message"]))
