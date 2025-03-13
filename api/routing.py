from django.urls import re_path
from api.consumers import ChildLocationConsumer

websocket_urlpatterns = [
    re_path(r'ws/live_location/$', ChildLocationConsumer.as_asgi()),
]
