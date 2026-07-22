import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.monitoring.permissions import verify_jwt


class MonitoringConsumer(AsyncWebsocketConsumer):
    CLINICAL_ROLES = {"professional", "nurse", "center_admin"}

    @classmethod
    def can_monitor(cls, payload, patient_id):
        role = payload.get("rol")
        return role in cls.CLINICAL_ROLES or (
            role == "patient" and str(payload.get("usuario_id")) == str(patient_id)
        )

    async def connect(self):
        self.patient_id = self.scope["url_route"]["kwargs"]["patient_id"]
        self.room_group_name = f"monitoring_{self.patient_id}"
        token = parse_qs(self.scope["query_string"].decode()).get("token", [None])[0]
        if not token:
            await self.close(code=4001); return
        try:
            payload = verify_jwt(token)
        except Exception:
            await self.close(code=4003); return
        if not self.can_monitor(payload, self.patient_id):
            await self.close(code=4003); return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def vital_update(self, event):
        await self.send(text_data=json.dumps({"type": "vital_update", "data": event["data"]}))

    async def alert_triggered(self, event):
        await self.send(text_data=json.dumps({"type": "alert", "data": event["data"]}))
