from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    """
    class Meta:
        model = Message
        fields = ('id', 'content', 'sender', 'created_at', 'sentiment_score')
        read_only_fields = ('id', 'created_at', 'sentiment_score')

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    """
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ('id', 'title', 'created_at', 'updated_at', 'messages', 'message_count')
        read_only_fields = ('id', 'created_at', 'updated_at', 'message_count')
    
    def get_message_count(self, obj):
        return obj.messages.count()

class ConversationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing conversations without including all messages.
    """
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ('id', 'title', 'created_at', 'updated_at', 'last_message', 'message_count')
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_message_count(self, obj):
        return obj.messages.count()

class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new message.
    """
    class Meta:
        model = Message
        fields = ('content', 'sender')
    
    def create(self, validated_data):
        conversation_id = self.context['conversation_id']
        return Message.objects.create(conversation_id=conversation_id, **validated_data)