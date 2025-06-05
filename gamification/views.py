from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    Quest, UserQuest, Achievement, UserAchievement,
    Reward, UserReward, UserPoints
)
from .serializers import (
    QuestSerializer, UserQuestSerializer, CompleteQuestSerializer,
    AchievementSerializer, UserAchievementSerializer,
    RewardSerializer, UserRewardSerializer, UserPointsSerializer,
    RedeemRewardSerializer
)
from .services.quest_service import get_recommended_quests
from .services.reward_service import generate_redemption_code

class QuestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing quests
    """
    queryset = Quest.objects.filter(is_active=True).order_by('id')
    serializer_class = QuestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_serializer_context(self):
        """Add request to serializer context for image URL generation"""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context  # Fixed: was returning only {'request': self.request}

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get quests recommended for the current user"""
        try:
            recommended_queryset = get_recommended_quests(request.user)
            recommended = recommended_queryset.order_by('id')[:5]
            serializer = self.get_serializer(recommended, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving recommended quests: {str(e)}")
            return Response({"error": "Failed to retrieve recommended quests"}, status=500)

        
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all quest categories"""
        from .models import QuestCategory
        categories = [
            {'value': category[0], 'display': category[1]}
            for category in QuestCategory.choices
        ]
        return Response(categories)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a quest"""
        quest = self.get_object()
        
        # Check if user already has this quest in progress
        existing = UserQuest.objects.filter(
            user=request.user,
            quest=quest,
            is_completed=False
        ).first()
        
        if existing:
            serializer = UserQuestSerializer(existing, context={'request': request})
            return Response(serializer.data)
        
        # Create new user quest
        mood_before = request.data.get('mood_before')
        user_quest = UserQuest.objects.create(
            user=request.user,
            quest=quest,
            mood_before=mood_before
        )
        
        serializer = UserQuestSerializer(user_quest, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserQuestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user quests
    """
    serializer_class = UserQuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only return quests for the current user"""
        return UserQuest.objects.filter(user=self.request.user).order_by('-started_at')  # Added ordering

    def get_serializer_context(self):
        """Add request to serializer context for image URL generation"""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a quest as completed"""
        user_quest = self.get_object()
        
        # Verify the quest is not already completed
        if user_quest.is_completed:
            return Response(
                {"detail": "Quest already completed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process the completion
        serializer = CompleteQuestSerializer(data=request.data)
        if serializer.is_valid():
            points_earned = user_quest.complete(
                reflection=serializer.validated_data.get('reflection', ''),
                mood_after=serializer.validated_data.get('mood_after')
            )
            
            # Update user points
            user_points, created = UserPoints.objects.get_or_create(user=request.user)
            user_points.add_points(points_earned)
            
            # Return the updated quest with points info
            result = UserQuestSerializer(user_quest, context={'request': request}).data
            result['points_earned'] = points_earned
            result['total_points'] = user_points.total_points
            result['current_points'] = user_points.current_points  # ADD THIS LINE
            return Response(result)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active (started but not completed) quests"""
        quests = self.get_queryset().filter(is_completed=False)
        serializer = self.get_serializer(quests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed quests"""
        quests = self.get_queryset().filter(is_completed=True)
        serializer = self.get_serializer(quests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get quests completed in the last 7 days"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        quests = self.get_queryset().filter(
            is_completed=True,
            completed_at__gte=seven_days_ago
        )
        serializer = self.get_serializer(quests, many=True)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        """Create a new user quest (start a quest)"""
        try:
            quest_id = request.data.get('quest_id')
            mood_before = request.data.get('mood_before')
            
            if not quest_id:
                return Response(
                    {"detail": "quest_id is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            quest = Quest.objects.get(id=quest_id, is_active=True)
            
            # Check if user already has this quest in progress
            existing = UserQuest.objects.filter(
                user=request.user,
                quest=quest,
                is_completed=False
            ).first()
            
            if existing:
                serializer = UserQuestSerializer(existing, context={'request': request})
                return Response(serializer.data)
            
            # Create new user quest
            user_quest = UserQuest.objects.create(
                user=request.user,
                quest=quest,
                mood_before=mood_before
            )
            
            serializer = UserQuestSerializer(user_quest, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Quest.DoesNotExist:
            return Response(
                {"detail": "Quest not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Log the actual error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating user quest: {str(e)}")
            return Response(
                {"detail": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing achievements
    """
    queryset = Achievement.objects.filter(is_active=True).order_by('id')  # Added ordering
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_serializer_context(self):
        """Add request to serializer context for image URL generation"""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=False, methods=['get'])
    def user_achievements(self, request):
        """Get achievements earned by the current user"""
        user_achievements = UserAchievement.objects.filter(user=request.user).order_by('-earned_at')  # Added ordering
        serializer = UserAchievementSerializer(user_achievements, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get achievements available to the user that haven't been earned yet"""
        # Get IDs of achievements already earned
        earned_ids = UserAchievement.objects.filter(user=request.user).values_list('achievement_id', flat=True)
        
        # Get achievements not yet earned
        available = Achievement.objects.filter(is_active=True).exclude(id__in=earned_ids).order_by('id')  # Added ordering
        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)

class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing and redeeming rewards
    """
    queryset = Reward.objects.filter(is_active=True).order_by('points_required', 'id')  # Added ordering
    serializer_class = RewardSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_serializer_context(self):
        """Add request to serializer context for image URL generation"""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=False, methods=['get'])
    def user_rewards(self, request):
        """Get rewards redeemed by the current user"""
        user_rewards = UserReward.objects.filter(user=request.user).order_by('-redeemed_at')  # Added ordering
        serializer = UserRewardSerializer(user_rewards, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get rewards available to the user"""
        # Get user's current points
        user_points, _ = UserPoints.objects.get_or_create(user=request.user)
        
        # Filter rewards that the user can afford
        available = self.get_queryset().filter(
            points_required__lte=user_points.current_points
        )
        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def redeem(self, request):
        """Redeem a reward"""
        serializer = RedeemRewardSerializer(data=request.data)
        if serializer.is_valid():
            reward_id = serializer.validated_data['reward_id']
            reward = get_object_or_404(Reward, id=reward_id, is_active=True)
            
            # Get user points
            user_points, _ = UserPoints.objects.get_or_create(user=request.user)
            
            # Check if user has enough points
            if user_points.current_points < reward.points_required:
                return Response(
                    {"detail": "Not enough points to redeem this reward."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate redemption code
            redemption_code = generate_redemption_code(reward, request.user)
            
            # Create user reward
            user_reward = UserReward.objects.create(
                user=request.user,
                reward=reward,
                redemption_code=redemption_code
            )
            
            # Spend points
            user_points.spend_points(reward.points_required)
            
            # Return the created user reward
            result_serializer = UserRewardSerializer(user_reward, context={'request': request})
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPointsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing user points
    """
    serializer_class = UserPointsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's points"""
        user_points, _ = UserPoints.objects.get_or_create(user=self.request.user)
        return UserPoints.objects.filter(id=user_points.id)

    def get_object(self):
        """Get the current user's points"""
        user_points, _ = UserPoints.objects.get_or_create(user=self.request.user)
        return user_points

    def list(self, request, *args, **kwargs):
        """Override list to return single object"""
        user_points, created = UserPoints.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(user_points)
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_streak(request):
    """Get user's current streak information"""
    user = request.user
    # Get all completed quests for this user, ordered by completion date
    completed_quests = UserQuest.objects.filter(
        user=user,
        is_completed=True
    ).order_by('-completed_at')

    if not completed_quests.exists():
        return Response({
            'current_streak': 0,
            'longest_streak': 0,
            'last_completion_date': None,
            'completed_today': False,
            'days_until_next_level': 7,
            'next_level_name': 'Week Warrior'
        })

    # Get unique completion dates
    completion_dates = set()
    for quest in completed_quests:
        if quest.completed_at:
            completion_dates.add(quest.completed_at.date())

    # Sort dates in descending order (most recent first)
    sorted_dates = sorted(completion_dates, reverse=True)

    # Calculate current streak
    current_streak = 0
    today = date.today()
    completed_today = today in completion_dates

    # Check if user completed a quest today or yesterday
    if sorted_dates[0] >= today - timedelta(days=1):
        current_streak = 1
        
        # Count consecutive days backwards from the most recent completion
        for i in range(1, len(sorted_dates)):
            expected_date = sorted_dates[i-1] - timedelta(days=1)
            if sorted_dates[i] == expected_date:
                current_streak += 1
            else:
                break

    # Calculate longest streak (simplified version)
    longest_streak = current_streak # You might want to implement a more complex calculation

    # Determine next level
    days_until_next_level = 0
    next_level_name = "Streak Master"
    
    if current_streak < 7:
        days_until_next_level = 7 - current_streak
        next_level_name = "Week Warrior"
    elif current_streak < 30:
        days_until_next_level = 30 - current_streak
        next_level_name = "Month Master"
    elif current_streak < 100:
        days_until_next_level = 100 - current_streak
        next_level_name = "Century Champion"

    return Response({
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'last_completion_date': sorted_dates[0].isoformat() if len(sorted_dates) > 0 else None,
        'completed_today': completed_today,
        'days_until_next_level': days_until_next_level,
        'next_level_name': next_level_name
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_completed_quest_dates(request):
    """Get list of dates when user completed quests"""
    user = request.user
    
    completed_quests = UserQuest.objects.filter(
        user=user,
        is_completed=True
    ).values_list('completed_at', flat=True)
    
    # Get unique dates
    unique_dates = set()
    for completed_at in completed_quests:
        unique_dates.add(completed_at.date())
    
    # Convert to ISO format strings
    date_strings = [date.isoformat() for date in sorted(unique_dates, reverse=True)]
    
    return Response(date_strings)    