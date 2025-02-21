import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def send_order_notification(event_type, order_data):
    try:
        channel_layer = get_channel_layer()
        logger.info(f"Sending {event_type} notification for order {order_data.get('uuid', 'unknown')}")
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
        logger.info("Notification sent successfully")
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}") 