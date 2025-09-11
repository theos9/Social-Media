from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import mixins
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, ConversationMember, Message
from account.models import User
from .serializers import ConversationSerializer, MessageSerializer
from djangochannelsrestframework.decorators import action
from channels.db import database_sync_to_async
from uuid import UUID
from django.core.serializers.json import DjangoJSONEncoder
import json

class ConversationConsumer(GenericAsyncAPIConsumer, mixins.ListModelMixin, mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin, mixins.DeleteModelMixin):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, **kwargs):
        return Conversation.objects.filter(members__user=self.scope["user"])

    def get_serializer_context(self, *args, **kwargs):
        context = super().get_serializer_context(*args, **kwargs)
        context["user"] = self.scope["user"]
        return context

    @action()
    async def add_member(self, request_id, conversation_id=None, user_id=None, role="member", **kwargs):
        try:
            UUID(str(conversation_id), version=4)
        except ValueError:
            return await self.reply(
                action="add_member",
                data={"message": "Invalid conversation_id"},
                request_id=request_id
            )
        try:
            conversation = await database_sync_to_async(Conversation.objects.get)(id=conversation_id)
        except Conversation.DoesNotExist:
            return await self.reply(
                action="add_member",
                data={"message": "Conversation not found"},
                request_id=request_id
            )
        try:
            member = await database_sync_to_async(ConversationMember.objects.get)(
                conversation=conversation, user=self.scope["user"]
            )
        except ValueError:
            return await self.reply(action="add_member", data={"message": "you are not in this conversation"}, request_id=request_id)
        if member.role not in ["owner", "admin"]:
            return await self.reply(action="add_member", data={"message": "Permission denied"}, request_id=request_id)
        try:
            user = await database_sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            return await self.reply(
                action="add_member",
                data={"message": "User not found"},
                request_id=request_id
            )
        if await database_sync_to_async(ConversationMember.objects.filter(conversation=conversation, user=user).exists)():
            return await self.reply(
                action="add_member",
                data={"message": "User is already a member of this conversation"},
                request_id=request_id
            )
        await database_sync_to_async(ConversationMember.objects.create)(
            conversation=conversation, user=user, role=role
        )
        await self.reply(
            action="remove_member",
            data={"message": f"User {user_id} added to conversation {conversation_id}"},
            request_id=request_id
        )

    @action()
    async def remove_member(self, request_id, conversation_id=None, user_id=None, **kwargs):
        try:
            UUID(str(conversation_id), version=4)
        except ValueError:
            return await self.reply(
                action="add_member",
                data={"message": "Invalid conversation_id"},
                request_id=request_id
            )
        try:
            conversation = await database_sync_to_async(Conversation.objects.get)(id=conversation_id)
        except Conversation.DoesNotExist:
            return await self.reply(
                action="add_member",
                data={"message": "Conversation not found"},
                request_id=request_id
            )
        try:
            member = await database_sync_to_async(ConversationMember.objects.get)(
                conversation=conversation, user=self.scope["user"]
            )
        except ValueError:
            return await self.reply(action="add_member", data={"message": "you are not in this conversation"}, request_id=request_id)
        if member.role not in ["owner", "admin"]:
            return await self.reply(action="add_member", data={"message": "Permission denied"}, request_id=request_id)
        try:
            user = await database_sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            return await self.reply(
                action="add_member",
                data={"message": "User not found"},
                request_id=request_id
            )
        if not await database_sync_to_async(ConversationMember.objects.filter(conversation=conversation, user=user).exists)():
            return await self.reply(
                action="add_member",
                data={"message": "User is not a member of this conversation"},
                request_id=request_id
            )
        await database_sync_to_async(ConversationMember.objects.filter(
            conversation=conversation, user=user
        ).delete)()
        await self.reply(
            action="remove_member",
            data={
                "message": f"User {user_id} removed from conversation {conversation_id}"},
            request_id=request_id
        )

class MessageConsumer(GenericAsyncAPIConsumer, mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,mixins.UpdateModelMixin):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    async def send_json(self, content, close=False):
        await super().send_json(json.loads(json.dumps(content, cls=DjangoJSONEncoder)), close=close)

    def get_queryset(self, **kwargs):
        user = self.scope["user"]
        return Message.objects.filter(
            conversation__members__user=user,
            sender=user,
            is_deleted=False
        )

    def get_serializer_context(self, *args, **kwargs):
        context = super().get_serializer_context(*args, **kwargs)
        context["user"] = self.scope["user"]
        return context
