from django.db import models
from users.models import CustomUser
import uuid
from orders.models import Order
from datetime import datetime, timedelta

# Create your models here.
class StoreProfile(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='store_profile')
    store_name = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    address = models.TextField()
    instagram_link = models.URLField(blank=True, null=True)
    twogis = models.URLField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    average_rating = models.FloatField(default=5.0)

    def __str__(self):
        return self.user.email
    
    def update_average_rating(self):
        from stores.models import Order  # Avoid circular import
        # Calculate the average rating for the store's completed orders
        result = Order.objects.filter(store=self.user, rating__isnull=False).aggregate(models.Avg('rating'))
        self.average_rating = result['rating__avg'] or 0.0  # Default to 0.0 if no ratings
        self.save()

class Price(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='prices')
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_accepted = models.BooleanField(default=False)  # True if the client accepts this price
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)  # Expiry time

    def save(self, *args, **kwargs):
        # Use datetime.now() if created_at is not yet set
        if not self.expires_at:
            self.expires_at = (self.created_at or datetime.now()) + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Price Proposal for Order {self.order.uuid}: {self.proposed_price}"

class Webhook(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='webhooks')
    url = models.URLField()  # The URL to send the webhook event to
    event_type = models.CharField(max_length=50)  # e.g., "price_proposed", "price_expired"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.event_type}"