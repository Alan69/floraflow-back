import uuid
from django.db import models
from django.utils import timezone

class Tariff(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default="Free", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена (тг)", default=0, null=True, blank=True)
    days = models.IntegerField(default=0)
    info = models.CharField(max_length=512, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    lasttimeactive = models.DateTimeField(null=True, blank=True, verbose_name="Дата покупки")

    def __str__(self):
        return f"{self.id} - {self.name}"
    
    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
