from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token['user_id'])
        return user
    except Exception:
        return None

class PriceNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Get token from query string
        query_string = parse_qs(self.scope['query_string'].decode())
        token = query_string.get('token', [None])[0]

        if token:
            user = await get_user_from_token(token)
            if user:
                self.user = user
                # Add user to a group
                await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
                if self.user.user_type == 'store':
                    await self.channel_layer.group_add("store_users", self.channel_name)
                await self.accept()
                return
        
        await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.channel_layer.group_discard(f"user_{self.user.id}", self.channel_name)
            if self.user.user_type == 'store':
                await self.channel_layer.group_discard("store_users", self.channel_name)

    async def send_notification(self, event):
        await self.send_json(event["data"])
