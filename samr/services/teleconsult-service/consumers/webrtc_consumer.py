import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.teleconsult.permissions import verify_jwt

class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_token = self.scope['url_route']['kwargs']['room_token']
        self.room_group_name = f'teleconsult_{self.room_token}'
        
        # Validar JWT por query string
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

    async def receive(self, text_data):
        """
        Recibe mensajes WebRTC (offer, answer, ice-candidate, chat) y los retransmite a la sala.
        """
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_message',
                'message': text_data_json,
                'sender_channel_name': self.channel_name
            }
        )

    async def webrtc_message(self, event):
        # No retransmitir el mensaje al propio remitente
        if self.channel_name != event.get('sender_channel_name'):
            await self.send(text_data=json.dumps(event['message']))
