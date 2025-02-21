import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)

class UUIDEncoder(DjangoJSONEncoder):
    def default(self, obj):
        from uuid import UUID
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

def send_order_notification(event_type, order_data):
    try:
        channel_layer = get_channel_layer()
        # Convert order_data to JSON-serializable format
        serialized_data = json.loads(json.dumps(order_data, cls=UUIDEncoder))
        logger.info(f"Sending {event_type} notification for order {serialized_data.get('uuid', 'unknown')}")
        
        async_to_sync(channel_layer.group_send)(
            "store_users",
            {
                "type": "send_notification",
                "data": {
                    "event": event_type,
                    "order": serialized_data
                }
            }
        )
        logger.info("Notification sent successfully")
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}") 