from rest_framework import serializers
from orders.models import Order
from stores.models import StoreProfile
from users.models import CustomUser

class StoreOrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.username', read_only=True)

    class Meta:
        model = Order
        fields = ['uuid', 'client_name', 'flower_data', 'price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'client_name', 'flower_data', 'created_at', 'updated_at']

class StoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProfile
        fields = ['uuid', 'logo', 'address', 'instagram_link']
