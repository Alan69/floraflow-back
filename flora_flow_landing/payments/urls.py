from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('tariffs/', views.TariffsView.as_view(), name='tariffs'),
    path('initiate/', views.InitiatePaymentView.as_view(), name='initiate'),
    path('status/', views.CheckPaymentStatusView.as_view(), name='status'),
] 