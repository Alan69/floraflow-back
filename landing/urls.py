from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('send-to-telegram/', views.send_to_telegram, name='send_to_telegram'),
]