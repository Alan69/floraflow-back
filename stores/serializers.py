from rest_framework import serializers
from orders.models import Order
from .models import StoreProfile, Price
from common.serializers import FlowerSerializer, ColorSerializer

class StoreOrderSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='client.first_name', read_only=True)
    flower = FlowerSerializer(read_only=True)
    color = ColorSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['uuid', 'first_name', 'flower', 'color', 'flower_height', 
                  'quantity', 'decoration', 'recipients_address', 'flower_data']
        read_only_fields = ['uuid', 'first_name', 'flower', 'color', 'flower_height', 
                            'quantity', 'decoration', 'recipients_address', 'flower_data']

class StoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProfile
        fields = ['uuid', 'store_name', 'logo', 'address', 'instagram_link', 'twogis', 'whatsapp_number', 'average_rating']
        read_only_fields = ['uuid', 'average_rating']

class PriceSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.store_profile.store_name', read_only=True)
    logo = serializers.ImageField(source='store.store_profile.logo', read_only=True)
    instagram_link = serializers.URLField(source='store.store_profile.instagram_link', read_only=True)
    whatsapp_number = serializers.CharField(source='store.store_profile.whatsapp_number', read_only=True)
    flower_img = serializers.ImageField(required=False)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.flower_img:
            representation['flower_img'] = instance.flower_img.url
        return representation

    class Meta:
        model = Price
        fields = ['uuid', 'proposed_price', 'flower_img', 'comment', 'is_accepted', 
                 'created_at', 'updated_at', 'expires_at', 'store_name', 'logo', 
                 'instagram_link', 'whatsapp_number']
        read_only_fields = ['uuid', 'is_accepted', 'expires_at', 'created_at', 'updated_at']