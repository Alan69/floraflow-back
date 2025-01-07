from django.db import models
from users.models import CustomUser
import uuid

# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_orders')
    store = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_orders')
    flower_data = models.TextField()  # Store details about the flowers
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.PositiveIntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return f"Order #{self.uuid} - {self.status}"