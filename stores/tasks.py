from celery import shared_task
from .models import StoreProfile

@shared_task
def update_store_ratings():
    stores = StoreProfile.objects.all()
    for store in stores:
        store.update_average_rating()
    return f"{stores.count()} store ratings updated."
