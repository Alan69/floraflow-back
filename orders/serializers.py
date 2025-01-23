from rest_framework import serializers
from .models import Order, Flower, Color

class FlowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flower
        fields = ['uuid', 'text']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['uuid', 'text']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'uuid', 
            'flower', 
            'color', 
            'flower_height', 
            'quantity',
            'decoration',
            'recipients_address', 
            'recipients_phone', 
            'flower_data',
            'price',
            'status', 
            'reason',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['uuid', 'status', 'price', 'reason', 'created_at', 'updated_at']

    def create(self, validated_data):
        client = self.context['request'].user
        validated_data['client'] = client
        return super().create(validated_data)

class OrderHistorySerializer(serializers.ModelSerializer):
    flower = FlowerSerializer()
    color = ColorSerializer()
    
    class Meta:
        model = Order
        fields = [
            'uuid', 
            'flower', 
            'color', 
            'flower_height', 
            'quantity', 
            'decoration',
            'city', 
            'recipients_address', 
            'recipients_phone', 
            'flower_data', 
            'price', 
            'status', 
            'reason',
            'created_at', 
            'updated_at',
            'rating'
        ]

class OrderRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['uuid', 'rating']
        read_only_fields = ['uuid']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value

    def update(self, instance, validated_data):
        if instance.status != 'completed':
            raise serializers.ValidationError("Оценить магазин можно только по выполненным заказам..")
        return super().update(instance, validated_data)