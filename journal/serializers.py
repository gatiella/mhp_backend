# journal/serializers.py
from rest_framework import serializers
from .models import Journal

class JournalSerializer(serializers.ModelSerializer):
    """
    Serializer for Journal model.
    """
    class Meta:
        model = Journal
        fields = ('id', 'title', 'content', 'mood_score', 'mood_note', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')