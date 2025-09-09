from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from .models import Conversation
from .serializers import ConversationSerializer


class ConversationConsumer(GenericAsyncAPIConsumer,ListModelMixin,CreateModelMixin):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self, **kwargs):
        return Conversation.objects.filter(members__user=self.scope["user"])
    def get_serializer_context(self, *args, **kwargs):
        context = super().get_serializer_context(*args, **kwargs)
        context["user"] = self.scope["user"]
        return context
