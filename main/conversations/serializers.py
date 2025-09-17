from rest_framework import serializers, status
from django.contrib.auth import get_user_model
from .models import Message, Conversation, ConversationMember
from uuid import UUID
User = get_user_model()


class ConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMember
        fields = ["user", "role"]


class ConversationSerializer(serializers.ModelSerializer):
    members = ConversationMemberSerializer(many=True, required=False)

    class Meta:
        model = Conversation
        fields = ["id", "type", "title", "description",
                  "is_public", "members", "creator"]
        extra_kwargs = {
            "creator": {"read_only": True},
            "id": {"read_only": True},
        }

    def validate(self, attrs):
        creator = self.context["user"]
        members_data = attrs.get("members", [])
        member_ids = [m["user"].id for m in members_data]
        conv_type = attrs.get("type") or getattr(self.instance, "type", None)
        is_public = attrs.get("is_public", getattr(
            self.instance, "is_public", False))

        if conv_type == "private" and member_ids:
            existing = Conversation.objects.filter(
                type="private", creator=creator, members__user__id=member_ids[0]).exists()
            reverse = Conversation.objects.filter(
                type="private", creator_id=member_ids[0], members__user__id=creator.id).exists()
            if existing or reverse:
                raise serializers.ValidationError(
                    "Private conversation with this user already exists.", code=status.HTTP_400_BAD_REQUEST)
        if conv_type == "private" and len(attrs.get("members", [])) > 1:
            raise serializers.ValidationError(
                "Private conversations can only have one member besides the creator.", code=status.HTTP_400_BAD_REQUEST)
        if conv_type in ["group", "channel"] and len(members_data) < 1:
            raise serializers.ValidationError(
                "Group and channel conversations must have at least one member besides the creator.", code=status.HTTP_400_BAD_REQUEST)
        if conv_type == "private" and "title" in attrs and attrs["title"]:
            raise serializers.ValidationError(
                "Private conversations cannot have a title.", code=status.HTTP_400_BAD_REQUEST)
        if conv_type == "private" and is_public:
            raise serializers.ValidationError(
                "Private conversations cannot be public.", code=status.HTTP_400_BAD_REQUEST)

        return attrs

    def create(self, validated_data):
        creator = self.context["user"]

        members_data = validated_data.pop("members", [])

        conversation = Conversation.objects.create(
            creator=creator, **validated_data
        )

        ConversationMember.objects.create(
            conversation=conversation, user=creator, role="owner"
        )

        for member_data in members_data:
            ConversationMember.objects.create(
                conversation=conversation, **member_data)

        return conversation


class MessageSerializer(serializers.ModelSerializer):
    conversation_id = serializers.UUIDField(write_only=True, required=False)
    delete = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Message
        fields = '__all__'
        extra_kwargs = {
            "id": {"read_only": True},
            "sender": {"read_only": True},
            "created_at": {"read_only": True},
            "is_edited": {"read_only": True},
            "is_deleted": {"read_only": True},
            "conversation": {"read_only": True},
        }

    def create(self, validated_data):
        sender = self.context["user"]
        content = validated_data.get("content")
        attachment = validated_data.get("attachment")
        reply_to = validated_data.get("reply_to")

        conversation_id = validated_data.pop("conversation_id")
        try:
            UUID(str(conversation_id), version=4)
        except ValueError:
            raise serializers.ValidationError("Invalid conversation_id",code=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation not found.",code=status.HTTP_404_NOT_FOUND)
        member = ConversationMember.objects.filter(conversation=conversation,user=sender).first()
        if not member.permissions.get("can_send", False):
            raise serializers.ValidationError("You don't have permission to send messages in this conversation.",code=status.HTTP_403_FORBIDDEN)
        if conversation.type == "channel" and member.role != "owner" and member.role != "admin":
            raise serializers.ValidationError("Only admins and owners can send messages in a channel.",code=status.HTTP_403_FORBIDDEN)
        if not content and not attachment:
            raise serializers.ValidationError(
                "Message must have either content or an attachment.",code=status.HTTP_400_BAD_REQUEST
            )

        if reply_to and reply_to.conversation_id != conversation_id:
            raise serializers.ValidationError(
                "Reply message must be in the same conversation.",code=status.HTTP_400_BAD_REQUEST
            )

        validated_data.pop("delete", None)

        message = Message.objects.create(
            sender=sender, conversation=conversation, **validated_data
        )
        return message

    def update(self, instance, validated_data):
        user = self.context["user"]
        conversation = instance.conversation
        member = ConversationMember.objects.get(
                conversation=conversation, user=user
            )
        if validated_data.get("delete", False):
            if member.permissions.get("can_delete", False):
                instance.is_deleted = True
            else:
                raise serializers.ValidationError("You don't have permission to delete messages in this conversation.",code=status.HTTP_403_FORBIDDEN)
        else:
            instance.content = validated_data.get("content", instance.content)
            instance.is_edited = True
        instance.save()
        return instance
