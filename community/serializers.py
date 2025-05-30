# backend/community/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    DiscussionGroup, DiscussionGroupMembership, ForumThread, ForumPost,
    Encouragement, CommunityChallenge, ChallengeParticipation,
    SuccessStory, StoryEncouragement
)
from .services.anonymizer_service import anonymize_user_data

User = get_user_model()


class AnonymousUserSerializer(serializers.ModelSerializer):
    """
    Serializer for anonymous user representation
    """
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['username']
    
    def get_username(self, obj):
        return anonymize_user_data(obj.username)


class DiscussionGroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    thread_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = DiscussionGroup
        fields = [
            'id', 'name', 'slug', 'description', 'topic_type', 
            'is_moderated', 'created_at', 'member_count', 
            'thread_count', 'is_member'
        ]
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_thread_count(self, obj):
        return obj.threads.count()
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False


class ForumThreadListSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    last_post_at = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumThread
        fields = [
            'id', 'title', 'discussion_group', 'created_by', 'author',
            'is_anonymous', 'is_pinned', 'is_locked', 'created_at', 
            'updated_at', 'post_count', 'last_post_at'
        ]
    
    def get_post_count(self, obj):
        return obj.posts.count()
    
    def get_author(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        elif obj.created_by:
            return obj.created_by.username
        return None
    
    def get_last_post_at(self, obj):
        last_post = obj.posts.order_by('-created_at').first()
        return last_post.created_at if last_post else obj.created_at


class ForumPostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    encouragement_count = serializers.SerializerMethodField()
    has_encouraged = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumPost
        fields = [
            'id', 'thread', 'content', 'author', 'author_name',
            'is_anonymous', 'created_at', 'updated_at',
            'encouragement_count', 'has_encouraged'
        ]
    
    def get_author_name(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        elif obj.author:
            return obj.author.username
        return None
    
    def get_encouragement_count(self, obj):
        return obj.encouragements.count()
    
    def get_has_encouraged(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.encouragements.filter(id=request.user.id).exists()
        return False


class ForumThreadDetailSerializer(serializers.ModelSerializer):
    posts = ForumPostSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumThread
        fields = [
            'id', 'title', 'discussion_group', 'created_by', 'author',
            'is_anonymous', 'is_pinned', 'is_locked', 'created_at', 
            'updated_at', 'posts'
        ]
    
    def get_author(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        elif obj.created_by:
            return obj.created_by.username
        return None


class EncouragementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encouragement
        fields = ['id', 'post', 'user', 'created_at', 'encouragement_type']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommunityChallengeSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()
    is_participating = serializers.SerializerMethodField()

    start_date = serializers.DateField(format=None)  # ⬅️ return ISO 8601
    end_date = serializers.DateField(format=None)
    created_at = serializers.DateTimeField(format=None)

    class Meta:
        model = CommunityChallenge
        fields = [
            'id', 'title', 'description', 'goal', 'start_date',
            'end_date', 'created_by', 'is_active', 'created_at',
            'challenge_type', 'participant_count', 'is_participating'
        ]

    def get_participant_count(self, obj):
        return obj.participants.count()

    def get_is_participating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(id=request.user.id).exists()
        return False
    
class SuccessStorySerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    encouragement_count = serializers.SerializerMethodField()
    has_encouraged = serializers.SerializerMethodField()
    
    class Meta:
        model = SuccessStory
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'is_anonymous', 'created_at', 'category',
            'encouragement_count', 'has_encouraged'
        ]
        read_only_fields = ['author', 'is_approved']
    
    def get_author_name(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        elif obj.author:
            return obj.author.username
        return None
    
    def get_encouragement_count(self, obj):
        return obj.encouragements.count()
    
    def get_has_encouraged(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.encouragements.filter(id=request.user.id).exists()
        return False
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class StoryEncouragementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryEncouragement
        fields = ['id', 'story', 'user', 'created_at']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)