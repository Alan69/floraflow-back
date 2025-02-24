from django.urls import re_path
from .consumers import PriceNotificationConsumer
from .consumers_folder.price_consumer import PriceConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', PriceNotificationConsumer.as_asgi()),
    re_path(r'ws/prices/$', PriceConsumer.as_asgi()),
]