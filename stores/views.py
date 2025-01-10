from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Order
from .serializers import StoreOrderSerializer, StoreProfileSerializer, PriceSerializer, WebhookSerializer
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.exceptions import PermissionDenied
from .models import Price
from stores.tasks import cancel_price_if_expired
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Endpoint to view client orders
class StoreOrdersView(generics.ListAPIView):
    serializer_class = StoreOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter orders for the logged-in store
        return Order.objects.filter(store=self.request.user).order_by('-created_at')

# Endpoint to update order price or send offers
class StoreOrderUpdateView(generics.CreateAPIView):
    """View for store users to propose a price for an order."""
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            raise NotAuthenticated("Для выполнения этого действия вам необходимо войти в систему.")

        # Ensure the user is a store
        if request.user.user_type != 'store':
            raise ValidationError("Только магазины могут предлагать цены.")

        # Get the `order_id` from the URL
        order_id = kwargs.get('order_id')

        # Validate if the order exists and belongs to the store
        try:
            order = Order.objects.get(uuid=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Extract the proposed price from the request data
        proposed_price = request.data.get('proposed_price')
        if not proposed_price:
            return Response({"error": "Предложенная цена обязательна."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the Price object
        price = Price.objects.create(order=order, proposed_price=proposed_price)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{order.client.id}",
            {
                "type": "send_notification",
                "data": {
                    "event": "price_proposed",
                    "price_id": str(price.uuid),
                    "proposed_price": str(price.proposed_price),
                    "order_id": str(order.uuid),
                },
            }
        )

        # Schedule a Celery task to check and cancel the proposal after 1 minute
        cancel_price_if_expired.apply_async((price.uuid,), countdown=60)

        # Return a success response
        return Response(
            {
                "detail": "Цена успешно предложена.",
                "price": PriceSerializer(price).data,
            },
            status=status.HTTP_201_CREATED,
        )

# Endpoint to update store profile
class StoreProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = StoreProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Check if the logged-in user is of type 'store'
        if self.request.user.user_type != 'store':
            raise PermissionDenied("У вас нет разрешения на доступ к этому ресурсу.")

        # Retrieve the store profile linked to the logged-in user
        try:
            return self.request.user.store_profile
        except AttributeError:
            raise PermissionDenied("Ни один профиль магазина не связан с этим пользователем..")

class WebhookRegistrationView(generics.CreateAPIView):
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)