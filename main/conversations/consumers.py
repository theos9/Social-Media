from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import permissions, mixins
from .models import Conversation , ConversationMember , Message
from .serializers import ConversationListSerializer , ConversationDetailSerializer , ConversationMemberSerializer 
import json
from django.core.serializers.json import DjangoJSONEncoder

class ConversationListCreateConsumer(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAsyncAPIConsumer):
    serializer_class = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self, **kwargs):
        user = self.scope["user"]
        return Conversation.objects.filter(creator=user)
    
class ConversationDetailConsumer(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DeleteModelMixin, GenericAsyncAPIConsumer):
    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    async def encode_json(self, content):
        return json.dumps(content, cls=DjangoJSONEncoder)
    
    def get_queryset(self, **kwargs):
        user = self.scope["user"]
        return Conversation.objects.filter(creator=user)
