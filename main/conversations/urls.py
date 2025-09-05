from django.urls import path
from .views import ConversationListCreateView , ConversationDetailView , SendMessageView

urlpatterns = [
    path('', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('<uuid:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('messages/', SendMessageView.as_view(), name='send-message'),
]
