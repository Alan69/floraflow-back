from rest_framework import serializers
from .models import Tariff

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['uuid', 'name', 'price', 'days', 'info', 'is_active']
        read_only_fields = ['uuid', 'name', 'price', 'days', 'info', 'is_active']