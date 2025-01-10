from channels.generic.websocket import AsyncJsonWebsocketConsumer

class PriceNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            # Add user to a group
            await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Remove user from the group
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(f"user_{self.user.id}", self.channel_name)

    async def send_notification(self, event):
        # Send data to the WebSocket
        await self.send_json(event["data"])
