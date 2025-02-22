from django.db import models
from users.models import CustomUser
import uuid
from orders.models import Order
from datetime import datetime, timedelta
from cloudinary.models import CloudinaryField
from django.utils import timezone

# Create your models here.
class StoreProfile(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='store_profile')
    store_name = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
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

def flower_image_path(instance, filename):
    # Generate path for flower images
    ext = filename.split('.')[-1]
    return f'flowers/{instance.uuid}/flower.{ext}'

class Price(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='prices')
    store = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_prices')
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    flower_img = models.ImageField(upload_to='price_logos/', blank=True, null=True)
    comment = models.TextField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False)  # True if the client accepts this price
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # If expires_at is naive, make it timezone-aware
        if self.expires_at and timezone.is_naive(self.expires_at):
            self.expires_at = timezone.make_aware(self.expires_at)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Price Proposal for Order {self.order.uuid}: {self.proposed_price}"