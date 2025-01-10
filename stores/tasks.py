from celery import shared_task
from .models import StoreProfile
from datetime import datetime
from stores.models import Price
from django.utils import timezone

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
        # Use timezone.now() for comparison
        if not price.is_accepted and price.expires_at <= timezone.now():
            price.delete()
            return f"Price {price_uuid} was canceled due to expiry."
    except Price.DoesNotExist:
        return f"Price {price_uuid} does not exist."