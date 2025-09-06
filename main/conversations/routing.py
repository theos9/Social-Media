from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/conversations/$', consumers.ConversationListCreateConsumer.as_asgi()),
    re_path(r'ws/conversations/(?P<pk>[^/]+)/$', consumers.ConversationDetailConsumer.as_asgi()),
    re_path(r'ws/messages/$', consumers.MessageConsumer.as_asgi()),
]