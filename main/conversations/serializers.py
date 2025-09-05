from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, Conversation, ConversationMember

User = get_user_model()
class ConversationMemberSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='user.phone', read_only=True)
    class Meta:
        model = ConversationMember
        fields = "__all__"

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.phone', read_only=True)
    receiver = serializers.CharField(source='receiver.phone', read_only=True)

    class Meta:
        model = Message
        fields = "__all__"

class ConversationDetailSerializer(serializers.ModelSerializer):
    members = ConversationMemberSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'type', 'creator', 'is_public', 'created_at', 'updated_at', 'members', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ConversationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']

class SendMessageSerializer(serializers.ModelSerializer):
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = ['content', 'receiver_id', 'attachment']

    def create(self, validated_data):
        sender = self.context['request'].user
        receiver_id = validated_data.pop('receiver_id')
        receiver = User.objects.get(id=receiver_id)

        conversation = Conversation.objects.filter(
            type='private',
            members__user=sender
        ).filter(
            members__user=receiver
        ).first()
        if not conversation:
            conversation = Conversation.objects.create(
                type='private',
                creator=sender
            )
            ConversationMember.objects.create(conversation=conversation, user=sender, role='owner')
            ConversationMember.objects.create(conversation=conversation, user=receiver, role='member')

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            receiver=receiver,
            **validated_data
        )

        return message
