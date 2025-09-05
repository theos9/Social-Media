from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import permissions, mixins
from .models import Conversation , ConversationMember , Message
from .serializers import ConversationListSerializer , ConversationDetailSerializer , ConversationMemberSerializer 

class ConversationListCreateConsumer(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAsyncAPIConsumer):
    serializer_class = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self, **kwargs):
        user = self.scope["user"]
        return Conversation.objects.filter(creator=user)
