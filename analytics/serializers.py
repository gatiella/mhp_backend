# analytics/serializers.py
from rest_framework import serializers
from mood.models import Mood
from journal.models import Journal
from conversation.models import Conversation

class MoodAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for mood analytics data.
    """
    date = serializers.DateField()
    avg_score = serializers.FloatField()
    count = serializers.IntegerField()

class UserActivitySerializer(serializers.Serializer):
    """
    Serializer for user activity data.
    """
    conversations_count = serializers.IntegerField()
    messages_count = serializers.IntegerField()
    journals_count = serializers.IntegerField()
    moods_count = serializers.IntegerField()
    conversation_minutes = serializers.FloatField()