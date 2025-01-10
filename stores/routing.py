from django.urls import re_path
from .consumers import PriceNotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', PriceNotificationConsumer.as_asgi()),
]
