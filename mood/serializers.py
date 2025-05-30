# mood/serializers.py
from rest_framework import serializers
from .models import Mood

class MoodSerializer(serializers.ModelSerializer):
    """
    Serializer for Mood model.
    """
    class Meta:
        model = Mood
        fields = ('id', 'score', 'note', 'created_at')
        read_only_fields = ('id', 'created_at')