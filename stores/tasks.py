from celery import shared_task
from .models import StoreProfile
import requests
from stores.models import Price
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def update_store_ratings():
    stores = StoreProfile.objects.all()
    for store in stores:
        store.update_average_rating()
    return f"{stores.count()} store ratings updated."


@shared_task
def cancel_price_if_expired(price_uuid):
    try:
        price = Price.objects.get(uuid=price_uuid)
        if not price.is_accepted and price.expires_at <= timezone.now():
            # Notify the client about price expiration
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{price.order.client.id}",
                {
                    "type": "send_notification",
                    "data": {
                        "event": "price_expired",
                        "price_id": str(price.uuid),
                        "expires_at": str(price.expires_at),
                    },
                }
            )
            price.delete()
            return f"Price {price_uuid} was canceled due to expiry."
    except Price.DoesNotExist:
        return f"Price {price_uuid} does not exist."