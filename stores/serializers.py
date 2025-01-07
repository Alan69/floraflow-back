from rest_framework import serializers
from orders.models import Order
from .models import StoreProfile, Price

class StoreOrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.username', read_only=True)
    prices = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['uuid', 'client_name', 'flower_data', 'price', 'status', 'created_at', 'updated_at', 'prices']
        read_only_fields = ['uuid', 'client_name', 'flower_data', 'status', 'created_at', 'updated_at']

    def get_prices(self, obj):
        return PriceSerializer(obj.prices.all(), many=True).data

class StoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProfile
        fields = ['uuid', 'store_name', 'logo', 'address', 'instagram_link', 'twogis', 'whatsapp_number', 'average_rating']
        read_only_fields = ['uuid', 'average_rating']

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['uuid', 'proposed_price', 'is_accepted', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'is_accepted', 'created_at', 'updated_at']