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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .pagination import CustomPagination
from django_filters import rest_framework as filters

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
            200: 'Пароль успешно обновлен',
            400: 'Invalid input data',
            401: 'Unauthorized',
        },
    )
    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Неправильный пароль'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Пароль успешно обновлен'}, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class AcceptPriceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Accept a price proposal for an order",
        responses={
            200: openapi.Response('Success', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example="Цена успешно принята.")
                }
            )),
            403: openapi.Response('Forbidden', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, example="У вас нет разрешения принять эту цену.")
                }
            )),
            404: openapi.Response('Not Found', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, example="Ценовое предложение не найдено или уже принято.")
                }
            ))
        },
        manual_parameters=[
            openapi.Parameter(
                'price_id',
                openapi.IN_PATH,
                description="UUID of the price proposal to accept",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        price_id = kwargs.get('price_id')  # Extract the price ID from the URL
        try:
            price = Price.objects.get(uuid=price_id, is_accepted=False)
        except Price.DoesNotExist:
            return Response({"error": "Ценовое предложение не найдено или уже принято."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the request user is the client associated with the order
        if request.user != price.order.client:
            return Response({"error": "У вас нет разрешения принять эту цену."}, status=status.HTTP_403_FORBIDDEN)

        # Mark the price as accepted
        price.is_accepted = True
        price.save()
    
        # Update the order's price
        price.order.store = price.store
        price.order.price = price.proposed_price
        price.order.status = 'accepted'
        price.order.save()

        return Response({"detail": "Цена успешно принята."}, status=status.HTTP_200_OK)
    
class PriceFilter(filters.FilterSet):
    class Meta:
        model = Price
        fields = {
            'is_accepted': ['exact'],
            'order__uuid': ['exact'],
        }

class UserProposedPriceListView(generics.ListAPIView):
    """View to list all proposed prices for the current user."""
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated]
    # pagination_class = CustomPagination
    # filter_backends = [DjangoFilterBackend, OrderingFilter]  # Add filtering and ordering backends
    # filterset_class = PriceFilter  # Fields you want to filter by
    # ordering_fields = ['created_at', 'updated_at', 'proposed_price']  # Fields you can order by
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        user = self.request.user

        # If user has no current order, return empty queryset
        if not user.current_order:
            return Price.objects.none()

        # If the user is a store, return prices they proposed for the current order
        if user.user_type == 'store':
            return Price.objects.filter(
                order=user.current_order,
                store=user
            )

        # If the user is a client, return prices proposed for their current order
        elif user.user_type == 'client':
            return Price.objects.filter(
                order=user.current_order,
                order__client=user
            )

        # Otherwise, return an empty queryset (e.g., for admins or invalid types)
        return Price.objects.none()

class CancelPriceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cancel a price proposal",
        responses={
            200: openapi.Response('Success', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example="Ценовое предложение успешно отменено.")
                }
            )),
            403: openapi.Response('Forbidden', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, example="У вас нет разрешения отменить это ценовое предложение.")
                }
            )),
            404: openapi.Response('Not Found', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, example="Ценовое предложение не найдено или уже принято.")
                }
            ))
        },
        manual_parameters=[
            openapi.Parameter(
                'price_id',
                openapi.IN_PATH,
                description="UUID of the price proposal to cancel",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        price_id = kwargs.get('price_id')
        try:
            price = Price.objects.get(uuid=price_id, is_accepted=False)
        except Price.DoesNotExist:
            return Response(
                {"error": "Ценовое предложение не найдено или уже принято."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the user has permission to cancel this price
        # Either the store who proposed it or the client who received it
        if request.user != price.store and request.user != price.order.client:
            return Response(
                {"error": "У вас нет разрешения отменить это ценовое предложение."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete the price proposal
        price.delete()

        return Response(
            {"detail": "Ценовое предложение успешно отменено."}, 
            status=status.HTTP_200_OK
        )