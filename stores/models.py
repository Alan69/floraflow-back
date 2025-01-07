from django.db import models
from users.models import CustomUser
import uuid
from orders.models import Order

# Create your models here.
class StoreProfile(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='store_profile')
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    address = models.TextField()
    instagram_link = models.URLField(blank=True, null=True)
    twogis = models.URLField(blank=True, null=True)
    whatsapp_number = status = models.CharField(max_length=20, blank=True, null=True)
    average_rating = models.FloatField(default=0.0)

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

    def __str__(self):
        return f"Price Proposal for Order {self.order.uuid}: {self.proposed_price}"