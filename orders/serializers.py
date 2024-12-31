from rest_framework import serializers
from .models import Order
from users.models import CustomUser

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'flower_data', 'price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        client = self.context['request'].user
        validated_data['client'] = client
        return super().create(validated_data)

class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'flower_data', 'price', 'status', 'created_at', 'updated_at']
