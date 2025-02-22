from rest_framework import serializers

from stores.serializers import PriceSerializerMe
from .models import Order
from common.serializers import FlowerSerializer, ColorSerializer, FlowerSerializerText, ColorSerializerText


class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.username', read_only=True)
    # uuid = serializers.UUIDField(format='hex')  # Add explicit UUID serialization
    
    class Meta:
        model = Order
        fields = ['uuid', 'client', 'client_name', 'flower', 'color', 'flower_height', 
                 'quantity', 'decoration', 'recipients_address', 'recipients_phone', 
                 'flower_data', 'status', 'created_at']
        read_only_fields = ['uuid', 'client', 'client_name']

    def create(self, validated_data):
        client = self.context['request'].user
        validated_data['client'] = client
        return super().create(validated_data)
    
class OrderSerializerDetail(serializers.ModelSerializer):
    flower = FlowerSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
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
        
class OrderSerializerDetailMe(serializers.ModelSerializer):
    flower = FlowerSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    prices = PriceSerializerMe(read_only=True, many=True)
    
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
            'store',
            'price',
            'prices',
            'status', 
            'reason',
            'created_at', 
            'updated_at'
        ]

class OrderHistorySerializer(serializers.ModelSerializer):
    flower = FlowerSerializerText()
    color = ColorSerializerText()
    store_name = serializers.CharField(source='store.store_profile.store_name', read_only=True)
    store_comment = serializers.SerializerMethodField()
    store_logo = serializers.ImageField(source='store.store_profile.logo', read_only=True)
    store_instagram_link = serializers.URLField(source='store.store_profile.instagram_link', read_only=True)
    store_whatsapp_number = serializers.CharField(source='store.store_profile.whatsapp_number', read_only=True)
    store_phone_number = serializers.CharField(source='store.phone', read_only=True)
    store_average_rating = serializers.FloatField(source='store.store_profile.average_rating', read_only=True)
    store_twogis = serializers.URLField(source='store.store_profile.twogis', read_only=True)

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
            'store_name',
            'store_comment',
            'store_logo',
            'store_instagram_link',
            'store_whatsapp_number',
            'store_phone_number',
            'store_average_rating',
            'store_twogis'
        ]

    def get_store_comment(self, obj):
        latest_price = obj.prices.order_by('-created_at').first()
        return latest_price.comment if latest_price else None

class OrderStoreHistorySerializer(serializers.ModelSerializer):
    flower = FlowerSerializerText()
    color = ColorSerializerText()
    proposed_price = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='client.first_name', read_only=True)
    customer_phone = serializers.CharField(source='client.phone', read_only=True)

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
            'status', 
            'reason',
            'created_at', 
            'updated_at',
            'rating',
            'proposed_price',
            'comment',
            'first_name',
            'customer_phone'
        ]

    def get_proposed_price(self, obj):
        price = obj.prices.first()  # Get the first price proposal
        return price.proposed_price if price else None

    def get_comment(self, obj):
        price = obj.prices.first()  # Get the first price proposal
        return price.comment if price else None

class OrderRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['uuid', 'rating']
        read_only_fields = ['uuid']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value