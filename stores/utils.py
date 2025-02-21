from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_order_notification(event_type, order_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "store_users",
        {
            "type": "send_notification",
            "data": {
                "event": event_type,
                "order": order_data
            }
        }
    ) 