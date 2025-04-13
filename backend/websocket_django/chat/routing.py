from django.urls import re_path
from .consumers import ChatConsumer
# from .consumers1 import DwsfChatConsumer
# from .consumers import ChatConsumerSonata

websocket_urlpatterns = [
    re_path(r'ws/chat/', ChatConsumer.as_asgi()),
    # re_path(r'ws/sonata/', ChatConsumerSonata.as_asgi()),
    # re_path(r'ws/dwsf/', DwsfChatConsumer.as_asgi())
]
