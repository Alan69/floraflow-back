from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from users.models import CustomUser

class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get token from query string
            query_string = self.scope['query_string'].decode()
            token = query_string.split('token=')[1] if 'token=' in query_string else None
            
            if not token:
                await self.close()
                return

            # Verify token and get user
            user = await self.get_user_from_token(token)
            if not user:
                await self.close()
                return

            self.user = user
            self.order = await self.get_current_order(user)
            
            if self.order:
                self.group_name = f'order_{self.order.uuid}'
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
            
            await self.accept()
            
        except Exception as e:
            print(f"WebSocket connection error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        pass

    async def price_update(self, event):
        await self.send(text_data=json.dumps({
            'event': event['event'],
            'price': event['price']
        }))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return CustomUser.objects.get(uuid=user_id)
        except Exception:
            return None

    @database_sync_to_async
    def get_current_order(self, user):
        return getattr(user, 'current_order', None) 