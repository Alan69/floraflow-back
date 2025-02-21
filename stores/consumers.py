from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
import logging

from users.models import CustomUser
logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user = CustomUser.objects.get(uuid=access_token['user_id'])
        return user
    except Exception as e:
        logger.error(f"Error authenticating WebSocket connection: {str(e)}")
        return None

class PriceNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            # Get token from query string
            query_string = parse_qs(self.scope['query_string'].decode())
            token = query_string.get('token', [None])[0]
            
            if not token:
                logger.error("No token provided in WebSocket connection")
                await self.close()
                return

            user = await get_user_from_token(token)
            if user:
                self.user = user
                await self.channel_layer.group_add(f"user_{self.user.uuid}", self.channel_name)
                if self.user.user_type == 'store':
                    await self.channel_layer.group_add("store_users", self.channel_name)
                await self.accept()
                logger.info(f"WebSocket connection accepted for user {user.uuid}")
                return
            
            logger.error("Invalid token or user not found")
            await self.close()
            
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.channel_layer.group_discard(f"user_{self.user.uuid}", self.channel_name)
            if self.user.user_type == 'store':
                await self.channel_layer.group_discard("store_users", self.channel_name)

    async def send_notification(self, event):
        """
        Send notification to WebSocket.
        """
        try:
            await self.send_json({
                "event": event["data"]["event"],
                "order": event["data"]["order"]
            })
            logger.info(f"Notification sent successfully: {event['data']['event']}")
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
