from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    UserRegistrationView,
    UserProfileView,
    UserChangePasswordView,
    CustomTokenObtainPairView,
    AcceptPriceView,
)

from orders.views import (
    OrderCreateView, 
    OrderHistoryView, 
    ClientProfileUpdateView
)

from stores.views import ( 
    StoreOrdersView, 
    StoreOrderUpdateView, 
    StoreProfileUpdateView )

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # users
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/change/', UserChangePasswordView.as_view(), name='change_password'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('prices/<uuid:price_id>/accept/', AcceptPriceView.as_view(), name='accept-price'),

    # stores
    path('store-orders/', StoreOrdersView.as_view(), name='store_orders'),
    path('store-order/<uuid:pk>/', StoreOrderUpdateView.as_view(), name='store_order_update'),
    path('store-profile/', StoreProfileUpdateView.as_view(), name='store_profile_update'),

    # orders
    path('order/', OrderCreateView.as_view(), name='order_create'),
    path('order-history/', OrderHistoryView.as_view(), name='order_history'),
    path('profile/', ClientProfileUpdateView.as_view(), name='profile_update'),
]
