from django.urls import re_path
from .consumers import ConversationConsumer, MessageConsumer

websocket_urlpatterns = [
    re_path(r"ws/conversations/$", ConversationConsumer.as_asgi()),
    re_path(r"ws/conversations/messages/$", MessageConsumer.as_asgi()),
]
