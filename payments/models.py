import uuid
from django.db import models
from django.utils import timezone

class Tariff(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default="Free", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена (тг)", default=0, null=True, blank=True)
    info = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        return f"{self.uuid} - {self.name}"
    
    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
