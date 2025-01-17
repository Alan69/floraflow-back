from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order, Flower, Color
from .serializers import OrderSerializer, OrderHistorySerializer, OrderRatingSerializer, FlowerSerializer, ColorSerializer

# Endpoint for creating a new order
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

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