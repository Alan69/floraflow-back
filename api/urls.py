from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    CancelPriceView,
    UserRegistrationView,
    UserProfileView,
    UserChangePasswordView,
    CustomTokenObtainPairView,
    AcceptPriceView,
    UserProposedPriceListView
)

from orders.views import (
    OrderCreateView, 
    OrderHistoryView,
    RateStoreView,
    FlowerListView,
    FlowerDetailView,
    ColorListView,
    ColorDetailView,
    CancelOrderView,
    OrderDetailView
)

from stores.views import ( 
    StoreOrderHistoryView,
    StoreOrderStatusView,
    StoreOrdersView, 
    StoreOrderUpdateView, 
    StoreProfileUpdateView
)

from payments.views import (
    get_tariffs,
    get_payment_token,
    initiate_payment,
    check_payment_status
)

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # users
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/change/', UserChangePasswordView.as_view(), name='change_password'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    
    # client prices
    path('client/prices/<uuid:price_id>/accept/', AcceptPriceView.as_view(), name='accept-price'),
    path('client/prices/<uuid:price_id>/cancel/', CancelPriceView.as_view(), name='cancel-price'),
    path('client/proposed-prices/', UserProposedPriceListView.as_view(), name='user-propose-prices'),

    # stores orders
    path('store/orders/', StoreOrdersView.as_view(), name='store_orders'),
    path('store/propose-price/<uuid:order_id>/', StoreOrderUpdateView.as_view(), name='propose-price'),
    path('store/profile/', StoreProfileUpdateView.as_view(), name='store_profile_update'),
    path('store/history/', StoreOrderHistoryView.as_view(), name='store_order_history'),
    path('store/order-status/<uuid:order_id>/', StoreOrderStatusView.as_view(), name='store_order_status'),

    # clien orders
    path('client/order/', OrderCreateView.as_view(), name='order_create'),
    path('client/order-history/', OrderHistoryView.as_view(), name='order_history'),
    path('client/order/<uuid:uuid>/rate/', RateStoreView.as_view(), name='rate-store'),
    path('client/<uuid:order_uuid>/cancel/', CancelOrderView.as_view(), name='cancel-order'),
    path('client/order/<uuid:uuid>/', OrderDetailView.as_view(), name='order_by_id'),

    # order data
    path('flowers/', FlowerListView.as_view(), name='flower-list'),
    path('flowers/<uuid:uuid>/', FlowerDetailView.as_view(), name='flower-detail'),
    path('colors/', ColorListView.as_view(), name='color-list'),
    path('colors/<uuid:uuid>/', ColorDetailView.as_view(), name='color-detail'),

    # payments
    path('tariffs/', get_tariffs, name='get_tariffs'),
    path('payment/token/', get_payment_token, name='get_payment_token'),
    path('payment/initiate/', initiate_payment, name='initiate_payment'),
    path('payment/status/', check_payment_status, name='check_payment_status'),
]
