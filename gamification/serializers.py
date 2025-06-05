from rest_framework import serializers
from .models import Quest, UserQuest, Achievement, UserAchievement, Reward, UserReward, UserPoints

class QuestSerializer(serializers.ModelSerializer):
    # Fix: Properly declare these as SerializerMethodField
    is_completed = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Quest
        fields = [
            'id', 'title', 'description', 'category', 'points',
            'duration_minutes', 'instructions', 'difficulty',
            'image', 'image_url', 'is_completed', 'progress'
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserQuest.objects.filter(
                user=request.user,
                quest=obj,
                is_completed=True
            ).exists()
        return False

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            quest = UserQuest.objects.filter(
                user=request.user,
                quest=obj
            ).first()
            return quest.progress if quest else 0.0
        return 0.0

# Rest of your serializers remain the same
class UserQuestSerializer(serializers.ModelSerializer):
    quest = QuestSerializer(read_only=True)
    quest_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserQuest
        fields = ['id', 'quest', 'quest_id', 'started_at', 'completed_at',
                 'is_completed', 'reflection', 'mood_before', 'mood_after']
        read_only_fields = ['started_at', 'completed_at', 'is_completed']

class CompleteQuestSerializer(serializers.Serializer):
    reflection = serializers.CharField(required=False, allow_blank=True)
    mood_after = serializers.IntegerField(required=False, min_value=1, max_value=5)

class AchievementSerializer(serializers.ModelSerializer):
    badge_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'category', 'badge_image', 'badge_image_url', 'points']

    def get_badge_image_url(self, obj):
        """Get the full URL for the badge image"""
        if obj.badge_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.badge_image.url)
            return obj.badge_image.url
        return None

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'earned_at']

class RewardSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Reward
        fields = ['id', 'title', 'description', 'points_required',
                 'partner_name', 'image', 'image_url', 'expiry_date']

    def get_image_url(self, obj):
        """Get the full URL for the image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class UserRewardSerializer(serializers.ModelSerializer):
    reward = RewardSerializer(read_only=True)

    class Meta:
        model = UserReward
        fields = ['id', 'reward', 'redeemed_at', 'redemption_code']

class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = ['total_points', 'current_points', 'last_updated']

class RedeemRewardSerializer(serializers.Serializer):
    reward_id = serializers.IntegerField()