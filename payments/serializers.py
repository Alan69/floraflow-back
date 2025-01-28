from rest_framework import serializers
from .models import Tariff

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['uuid', 'name', 'price', 'info']
        read_only_fields = ['uuid', 'name', 'price', 'info']