from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Order
from .serializers import StoreOrderSerializer, StoreProfileSerializer, PriceSerializer
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.exceptions import PermissionDenied
from .models import Price
from stores.tasks import cancel_price_if_expired
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from orders.serializers import OrderSerializer
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Endpoint to view client orders
class StoreOrdersView(generics.ListAPIView):
    serializer_class = StoreOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter orders for the logged-in store
        return Order.objects.filter(status='pending').order_by('-created_at')

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

        # Ensure the store has a profile
        try:
            store_profile = request.user.store_profile
        except AttributeError:
            raise ValidationError("У магазина должен быть настроен профиль для предложения цен.")

        # Get the `order_id` from the URL
        order_id = kwargs.get('order_id')

        # Validate if the order exists
        try:
            order = Order.objects.get(uuid=order_id)
            # Associate the store with the order if not already set
            if not order.store:
                order.store = request.user
                order.save()
        except Order.DoesNotExist:
            return Response({"error": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Extract the proposed price from the request data
        proposed_price = request.data.get('proposed_price')
        flower_img = request.data.get('flower_img')  # Get flower_img if provided
        comment = request.data.get('comment')  # Get comment if provided
        if not proposed_price:
            return Response({"error": "Предложенная цена обязательна."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the Price object
        price = Price.objects.create(
            order=order,
            proposed_price=proposed_price,
            flower_img=flower_img,
            comment=comment,
            store = request.user
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{order.client.uuid}",
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

class StoreOrderHistoryView(generics.ListAPIView):
    """
    API endpoint that allows stores to view their order history.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get store order history with optional status filtering",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter orders by status. Use 'all' for all orders.",
                type=openapi.TYPE_STRING,
                enum=['all', 'pending', 'accepted', 'in_transit', 'completed', 'canceled'],
                default='all'
            ),
        ],
        responses={
            200: OrderSerializer(many=True),
            403: "Permission denied - Only store users can access order history",
            400: "Invalid status parameter"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return filtered orders for the current store based on status
        """
        if self.request.user.user_type != 'store':
            raise PermissionDenied("Only store users can access order history.")
            
        # Get status filter from query params
        status = self.request.query_params.get('status', 'all')
        
        # Base queryset
        queryset = Order.objects.filter(store=self.request.user)
        
        # Filter by status if a valid status is provided
        if status != 'all':
            if status in dict(Order.STATUS_CHOICES):
                queryset = queryset.filter(status=status)
            else:
                raise ValidationError(f"Invalid status. Must be one of: {', '.join(dict(Order.STATUS_CHOICES).keys())}")
            
        return queryset.order_by('-created_at')

class StoreOrderStatusView(APIView):
    """
    API endpoint that allows stores to update the status of their orders.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Update the status of a specific order",
        manual_parameters=[
            openapi.Parameter(
                'order_id',
                openapi.IN_PATH,
                description="ID of the order to update",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status'],
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['accepted', 'in_progress', 'ready', 'completed', 'cancelled'],
                    description="New status for the order"
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Order status updated successfully",
                examples={
                    "application/json": {
                        "message": "Order status updated successfully",
                        "status": "accepted"
                    }
                }
            ),
            400: "Invalid status or missing status",
            403: "Permission denied",
            404: "Order not found"
        }
    )
    def patch(self, request, order_id):
        """
        Update the status of a specific order.

        Parameters:
            - order_id (int): The ID of the order to update
            - status (str): The new status for the order. Must be one of:
                * accepted
                * in_progress
                * ready
                * completed
                * cancelled

        Returns:
            - 200: Order status updated successfully
            - 400: Invalid status or missing status
            - 403: Permission denied
            - 404: Order not found
        """
        try:
            order = Order.objects.get(id=order_id)
            new_status = request.data.get('status')
            
            if not new_status:
                return Response(
                    {'error': 'Status is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate status is one of the allowed values
            allowed_statuses = ['accepted', 'in_progress', 'ready', 'completed', 'cancelled']
            if new_status not in allowed_statuses:
                return Response(
                    {'error': f'Invalid status. Must be one of: {", ".join(allowed_statuses)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if the store owns this order
            if order.store != request.user.store:
                return Response(
                    {'error': 'You do not have permission to update this order'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            order.status = new_status
            order.save()
            
            return Response({
                'message': 'Order status updated successfully',
                'status': new_status
            })
            
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )