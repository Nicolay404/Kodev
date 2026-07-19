import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.monitoring.permissions import verify_jwt

class MonitoringConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.patient_id = self.scope['url_route']['kwargs']['patient_id']
        self.room_group_name = f'monitoring_{self.patient_id}'
        
        # Extraer token de query string: ?token=xyz
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        if not token:
            await self.close(code=4001)
            return
            
        try:
            payload = verify_jwt(token)
            self.user_id = payload.get('usuario_id')
        except Exception:
            await self.close(code=4003)
            return

        # Unirse a la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Recibir mensaje del grupo para actualización de signos vitales
    async def vital_update(self, event):
        data = event['data']
        
        await self.send(text_data=json.dumps({
            'type': 'vital_update',
            'data': data
        }))
        
    # Recibir mensaje de alerta del grupo
    async def alert_triggered(self, event):
        data = event['data']
        
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'data': data
        }))
