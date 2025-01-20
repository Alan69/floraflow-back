from django.db import models
from users.models import CustomUser
import uuid

class Flower(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.text}"

class Color(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.text}"

# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('accepted', 'В пути'),
        ('completed', 'Доставлен'),
        ('canceled', 'Отменен'),
    ]

    FLOWER_HEIGHT_CHOICES = [
        ('50cm', '50cm'),
        ('60cm', '60cm'),
        ('70cm', '70cm'),
        ('80cm', '80cm'),
        ('90cm', '90cm'),
        ('100cm', '100cm'),
        ('110cm', '110cm'),
        ('120cm', '120cm'),
        ('130cm', '130cm'),
        ('140cm', '140cm'),
        ('150cm', '150cm'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_orders')
    store = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_orders', null=True, blank=True)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE, related_name='flower', null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='color', null=True, blank=True)
    flower_height = models.CharField(max_length=20, choices=FLOWER_HEIGHT_CHOICES)
    quantity = models.PositiveIntegerField()
    decoration = models.BooleanField(default=False)
    city = models.CharField(max_length=255, default="Астана")
    recipients_address = models.CharField(max_length=255)
    recipients_phone = models.CharField(max_length=15)
    flower_data = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.PositiveIntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return f"Order #{self.uuid} - {self.status}"