from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Order
from .serializers import StoreOrderSerializer, StoreProfileSerializer, PriceSerializer
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.exceptions import PermissionDenied
from .models import Price

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
            raise NotAuthenticated("You must be logged in to perform this action.")

        # Ensure the user is a store
        if request.user.user_type != 'store':
            raise ValidationError("Only store users can propose prices.")

        # Get the `order_id` from the URL
        order_id = kwargs.get('order_id')

        # Validate if the order exists and belongs to the store
        try:
            order = Order.objects.get(uuid=order_id, store=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or not associated with your store."}, status=status.HTTP_404_NOT_FOUND)

        # Extract the proposed price from the request data
        proposed_price = request.data.get('proposed_price')
        if not proposed_price:
            return Response({"error": "Proposed price is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the Price object
        price = Price.objects.create(order=order, proposed_price=proposed_price)

        # Return a success response
        return Response(
            {
                "detail": "Price proposed successfully.",
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
            raise PermissionDenied("You do not have permission to access this resource.")

        # Retrieve the store profile linked to the logged-in user
        try:
            return self.request.user.store_profile
        except AttributeError:
            raise PermissionDenied("No store profile is associated with this user.")
