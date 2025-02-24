from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from orders.models import Order

class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get token from query string
        token = self.scope['query_string'].decode().split('token=')[1]
        
        try:
            # Verify token and get user
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await self.get_user(user_id)
            
            if not self.user:
                await self.close()
                return
                
            # Add to price group for the user's current order
            if self.user.current_order:
                self.order_group_name = f'order_{self.user.current_order.uuid}'
                await self.channel_layer.group_add(
                    self.order_group_name,
                    self.channel_name
                )
                
            await self.accept()
            
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'order_group_name'):
            await self.channel_layer.group_discard(
                self.order_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        pass  # We don't need to handle incoming messages for this consumer

    async def price_update(self, event):
        # Send price update to WebSocket
        await self.send(text_data=json.dumps({
            'event': event['event'],
            'price': event['price']
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None 