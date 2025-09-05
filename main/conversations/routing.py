from django.urls import re_path
from .consumers import ConversationListCreateConsumer , ConversationDetailConsumer

websocket_urlpatterns = [
    re_path(r"ws/conversations/list/$", ConversationListCreateConsumer.as_asgi()),
    re_path(r"ws/conversations/detail/$", ConversationDetailConsumer.as_asgi()),
]