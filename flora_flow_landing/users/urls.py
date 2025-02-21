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
] 