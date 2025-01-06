from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Order
from .serializers import StoreOrderSerializer, StoreProfileSerializer
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.exceptions import PermissionDenied

# Endpoint to view client orders
class StoreOrdersView(generics.ListAPIView):
    serializer_class = StoreOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter orders for the logged-in store
        return Order.objects.filter(store=self.request.user).order_by('-created_at')

# Endpoint to update order price or send offers
class StoreOrderUpdateView(generics.UpdateAPIView):
    serializer_class = StoreOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Short-circuit during Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()  # Return an empty queryset for Swagger

        # Check if the user is authenticated
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("You must be logged in to access this endpoint.")

        # Ensure the user is a store
        if self.request.user.user_type != 'store':
            raise ValidationError("Only store users can update orders.")

        # Return orders for the authenticated store user
        return Order.objects.filter(store=self.request.user)

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Extract the proposed price from the request data
        proposed_price = request.data.get('proposed_price')
        if not proposed_price:
            return Response({"error": "Proposed price is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Price object
        price = Price.objects.create(order=order, proposed_price=proposed_price)

        return Response({"detail": "Price proposed successfully.", "price_id": price.uuid}, status=status.HTTP_201_CREATED)

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
