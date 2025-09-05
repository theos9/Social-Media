from rest_framework import generics, permissions
from .models import Message, Conversation
from .serializers import ConversationDetailSerializer , ConversationListSerializer, SendMessageSerializer

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(creator=user)

class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(creator=user)
    
class SendMessageView(generics.CreateAPIView):
    serializer_class = SendMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
