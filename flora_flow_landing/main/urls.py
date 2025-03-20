from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('send-to-telegram/', views.send_to_telegram, name='send_to_telegram'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('contact/', views.contact, name='contact'),
    path('send-support-message/', views.send_support_message, name='send_support_message'),
]