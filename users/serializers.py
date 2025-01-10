from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cloudinary.utils import cloudinary_url

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'city']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            city=validated_data.get('city', None),
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and updating user profile."""
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'user_type', 'city', 'profile_picture']
        read_only_fields = ['email']  # Prevent updating email and user type

    def get_profile_picture(self, obj):
        """Return the full URL for the profile picture."""
        if obj.profile_picture:
            # Build the full URL using Cloudinary utilities
            return f"https://res.cloudinary.com/dwbv1fvgp/image/upload/v1736420569/{obj.profile_picture}"
        return None  # Return None if no picture is uploaded


class UserChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("Новый пароль не может совпадать со старым паролем..")
        return data

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        data['user'] = UserProfileSerializer(user).data

        return data