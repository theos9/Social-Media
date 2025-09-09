from rest_framework import serializers , status
from django.contrib.auth import get_user_model
from .models import Message, Conversation, ConversationMember

User = get_user_model()

class ConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMember
        fields = ["user", "role"]

class ConversationSerializer(serializers.ModelSerializer):
    members = ConversationMemberSerializer(many=True, write_only=True)
    class Meta:
        model = Conversation
        fields = ["id", "type", "title", "description", "is_public", "members", "creator"]
        extra_kwargs = {
            "creator": {"read_only": True}
        }
    def validate(self, attrs):
        creator = self.context["user"]
        members_data = attrs.get("members", [])
        member_ids = [m["user"].id for m in members_data]

        if attrs.get("type") == "private" and member_ids:
            existing = Conversation.objects.filter(type="private", creator=creator, members__user__id=member_ids[0]).exists()
            reverse  = Conversation.objects.filter(type="private", creator_id=member_ids[0], members__user__id=creator.id).exists()
            if existing or reverse :
                raise serializers.ValidationError("Private conversation with this user already exists.",code=status.HTTP_400_BAD_REQUEST)
        if attrs.get("type") == "private" and len(attrs.get("members", [])) > 1:
            raise serializers.ValidationError("Private conversations can only have one member besides the creator.",code=status.HTTP_400_BAD_REQUEST)
        if attrs.get("type") in ["group", "channel"] and len(attrs.get("members", [])) < 1:
            raise serializers.ValidationError("Group and channel conversations must have at least one member besides the creator.",code=status.HTTP_400_BAD_REQUEST)
        if attrs.get("type") == "private" and attrs.get("title"):
            raise serializers.ValidationError("Private conversations cannot have a title.",code=status.HTTP_400_BAD_REQUEST)
        if attrs.get("type") == "private" and attrs.get("is_public"):
            raise serializers.ValidationError("Private conversations cannot be public.",code=status.HTTP_400_BAD_REQUEST)
        

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
            ConversationMember.objects.create(conversation=conversation, **member_data)

        return conversation
    