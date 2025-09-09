from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import mixins
from rest_framework.permissions import IsAuthenticated
from .models import Conversation
from .serializers import ConversationSerializer


class ConversationConsumer(GenericAsyncAPIConsumer,mixins.ListModelMixin,mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,mixins.DeleteModelMixin):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self, **kwargs):
        return Conversation.objects.filter(members__user=self.scope["user"])
    def get_serializer_context(self, *args, **kwargs):
        context = super().get_serializer_context(*args, **kwargs)
        context["user"] = self.scope["user"]
        return context
