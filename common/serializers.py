from rest_framework import serializers
from orders.models import Flower, Color

class FlowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flower
        fields = ['uuid', 'text']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['uuid', 'text']

class FlowerSerializerText(serializers.ModelSerializer):
    class Meta:
        model = Flower
        fields = ['text']  # Include only the 'text' field


class ColorSerializerText(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['text']  # Include only the 'text' field