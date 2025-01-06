from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from stores.models import Price
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserChangePasswordSerializer,
    CustomTokenObtainPairSerializer
)
from stores.serializers import PriceSerializer

class UserRegistrationView(generics.CreateAPIView):
    """Endpoint for user registration."""
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response('User registered successfully', UserProfileSerializer),
            400: 'Invalid input data',
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Endpoint for retrieving and updating user profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the currently authenticated user
        return self.request.user

    @swagger_auto_schema(
        operation_description="Retrieve the authenticated user's profile",
        responses={
            200: UserProfileSerializer,
            401: 'Unauthorized',
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update the authenticated user's profile",
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: 'Invalid input data',
            401: 'Unauthorized',
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class UserChangePasswordView(generics.UpdateAPIView):
    """Endpoint for changing user password."""
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change the authenticated user's password",
        request_body=UserChangePasswordSerializer,
        responses={
            200: 'Password updated successfully',
            400: 'Invalid input data',
            401: 'Unauthorized',
        },
    )
    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password updated successfully'}, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class AcceptPriceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        price_id = kwargs.get('price_id')  # Extract the price ID from the URL
        try:
            price = Price.objects.get(uuid=price_id, is_accepted=False)
        except Price.DoesNotExist:
            return Response({"error": "Price proposal not found or already accepted."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the request user is the client associated with the order
        if request.user != price.order.client:
            return Response({"error": "You do not have permission to accept this price."}, status=status.HTTP_403_FORBIDDEN)

        # Mark the price as accepted
        price.is_accepted = True
        price.save()

        # Update the order's price
        price.order.price = price.proposed_price
        price.order.save()

        return Response({"detail": "Price accepted successfully."}, status=status.HTTP_200_OK)
    
class UserProposedPriceListView(generics.ListAPIView):
    """View to list all proposed prices for the current user."""
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # If the user is a store, return prices they proposed
        if user.user_type == 'store':
            return Price.objects.filter(order__store=user)

        # If the user is a client, return prices proposed for their orders
        elif user.user_type == 'client':
            return Price.objects.filter(order__client=user)

        # Otherwise, return an empty queryset (e.g., for admins or invalid types)
        return Price.objects.none()