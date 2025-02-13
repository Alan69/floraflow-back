from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order, Flower, Color
from .serializers import OrderSerializer, OrderHistorySerializer, OrderRatingSerializer, FlowerSerializer, ColorSerializer, OrderSerializerDetail
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError

# Endpoint for creating a new order
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.current_order:
            raise ValidationError("You already have an active order.")
        
        order = serializer.save(client=self.request.user)
        self.request.user.current_order = order
        self.request.user.save()

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializerDetail
    lookup_field = 'uuid'

# Endpoint for viewing order history
class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user).order_by('-created_at')

class RateStoreView(generics.UpdateAPIView):
    """View to allow clients to rate a store for a completed order."""
    serializer_class = OrderRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()  # Return an empty queryset

        return Order.objects.filter(client=self.request.user, status='completed')

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Ensure the client is rating their own order
        if order.client != request.user:
            return Response(
                {"error": "Вы можете давать оценку только своим заказам."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

class FlowerListView(generics.ListAPIView):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer

class FlowerDetailView(generics.RetrieveAPIView):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer
    lookup_field = 'uuid'

class ColorListView(generics.ListAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class ColorDetailView(generics.RetrieveAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    lookup_field = 'uuid'

class CancelOrderView(APIView):
    @swagger_auto_schema(
        operation_summary="Cancel an Order",
        operation_description="Allows a user to cancel an order by providing an optional cancellation reason. The order's status will be updated to 'canceled'.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The reason for canceling the order (optional).",
                    example="Changed my mind about the purchase"
                ),
            },
            required=[]  # Changed from ['reason'] to make it optional
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    "order": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "uuid": openapi.Schema(type=openapi.TYPE_STRING, description="Order UUID"),
                            "status": openapi.Schema(type=openapi.TYPE_STRING, description="Order status"),
                            "reason": openapi.Schema(type=openapi.TYPE_STRING, description="Reason for cancellation"),
                        },
                    ),
                },
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                },
            ),
        }
    )
    def post(self, request, order_uuid):
        # Fetch the order by UUID
        order = get_object_or_404(Order, uuid=order_uuid)
        
        user = request.user

        # Check if the order is already canceled or completed
        if order.status in ['canceled', 'completed']:
            return Response(
                {"detail": f"Order is already {order.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the cancellation reason from the request, default to empty string if null/blank
        reason = request.data.get('reason', '').strip() if request.data.get('reason') else ''

        # Update the order status and add the cancellation reason
        user.current_order = None
        user.save()
        order.status = 'canceled'
        order.reason = reason
        order.save()

        return Response(
            {"detail": "Order canceled successfully.", "order": OrderSerializer(order).data},
            status=status.HTTP_200_OK
        )
