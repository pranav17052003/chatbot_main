import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'websocket_django.settings')
import django 
django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing  # Import routing from your chat app



application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns  # Correct routing for your WebSocket connection
        )
    ),
})
