from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Order
from .serializers import StoreOrderSerializer, StoreProfileSerializer
from rest_framework.exceptions import NotAuthenticated

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

        # Return orders for the authenticated store user
        return Order.objects.filter(store=self.request.user)

# Endpoint to update store profile
class StoreProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = StoreProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the store profile linked to the logged-in user
        return self.request.user.store_profile
