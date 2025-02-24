from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('store-profile/', views.StoreProfileView.as_view(), name='store_profile_update'),
    path('create-order/', views.CreateOrderView.as_view(), name='create_order'),
    path('cancel-order/<uuid:order_uuid>/', views.CancelOrderView.as_view(), name='cancel_order'),
    path('order-history/', views.OrderHistoryView.as_view(), name='order_history'),
    path('rate-store/<uuid:uuid>/', views.RateStoreView.as_view(), name='rate-store'),
    path('store-orders/', views.StoreOrdersView.as_view(), name='store_orders'),
    path('store-order-history/', views.StoreOrderHistoryView.as_view(), name='store_order_history'),
    path('propose-price/<uuid:order_id>/', views.ProposePriceView.as_view(), name='propose-price'),
    path('current-order/', views.CurrentOrderView.as_view(), name='current_order'),
    path('client/proposed-prices/', views.ClientProposedPricesView.as_view(), name='client_proposed_prices'),
    path('client/accept-price/<uuid:price_id>/', views.AcceptPriceView.as_view(), name='accept-price'),
    path('client/cancel-price/<uuid:price_id>/', views.CancelPriceView.as_view(), name='cancel-price'),
    path('store/order-status/<uuid:order_uuid>/', views.StoreOrderStatusUpdateView.as_view(), name='store_order_status'),
] 