from rest_framework import serializers
from .models import Order
from users.models import CustomUser

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['uuid', 'flower_data', 'price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        client = self.context['request'].user
        validated_data['client'] = client
        return super().create(validated_data)

class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['uuid', 'flower_data', 'price', 'status', 'created_at', 'updated_at']

class OrderRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['uuid', 'rating']
        read_only_fields = ['uuid']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def update(self, instance, validated_data):
        if instance.status != 'completed':
            raise serializers.ValidationError("You can only rate a store for completed orders.")
        return super().update(instance, validated_data)