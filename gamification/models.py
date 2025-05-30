from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import date, timedelta

class QuestCategory(models.TextChoices):
    CBT = 'cbt', 'Cognitive Behavioral Therapy'
    MINDFULNESS = 'mindfulness', 'Mindfulness'
    ACTIVITY = 'activity', 'Physical Activity'
    SOCIAL = 'social', 'Social Connection'
    GRATITUDE = 'gratitude', 'Gratitude Practice'

class Quest(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=QuestCategory.choices,
        default=QuestCategory.MINDFULNESS
    )
    points = models.IntegerField(default=10)
    duration_minutes = models.IntegerField(default=5)
    instructions = models.TextField()
    difficulty = models.IntegerField(default=1)  # 1-5 scale
    # Change CharField to ImageField
    image = models.ImageField(upload_to='quest_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class UserQuest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    reflection = models.TextField(null=True, blank=True)
    mood_before = models.IntegerField(null=True, blank=True)  # 1-5 scale
    mood_after = models.IntegerField(null=True, blank=True)  # 1-5 scale
    
    def complete(self, reflection="", mood_after=None):
        self.completed_at = timezone.now()
        self.is_completed = True
        self.reflection = reflection
        self.mood_after = mood_after
        self.save()
        
        # Create achievement progress
        self._update_achievements()
        
        return self.quest.points
    
    def _update_achievements(self):
        """Update user's progress toward achievements based on completed quest"""
        # Count completed quests in this category
        category_count = UserQuest.objects.filter(
            user=self.user,
            quest__category=self.quest.category,
            is_completed=True
        ).count()
        
        # Check for streak achievements
        # Get all completed quests for this user, ordered by completion date
        completed_quests = UserQuest.objects.filter(
            user=self.user,
            is_completed=True
        ).order_by('-completed_at')

        if completed_quests.exists():
            # Get unique completion dates
            completion_dates = set()
            for quest in completed_quests:
                completion_dates.add(quest.completed_at.date())
            
            # Sort dates in descending order (most recent first)
            sorted_dates = sorted(completion_dates, reverse=True)
            
            # Calculate current streak
            current_streak = 0
            today = date.today()
            
            # Check if user completed a quest today or yesterday (to account for timezone differences)
            if sorted_dates[0] >= today - timedelta(days=1):
                current_streak = 1
                
                # Count consecutive days backwards from the most recent completion
                for i in range(1, len(sorted_dates)):
                    expected_date = sorted_dates[i-1] - timedelta(days=1)
                    if sorted_dates[i] == expected_date:
                        current_streak += 1
                    else:
                        break
            
            # Check for streak-based achievements
            streak_achievements = Achievement.objects.filter(
                title__icontains='streak',  # Assumes streak achievements have 'streak' in title
                required_count__lte=current_streak,
                is_active=True
            )
            
            for achievement in streak_achievements:
                if not UserAchievement.objects.filter(user=self.user, achievement=achievement).exists():
                    UserAchievement.objects.create(
                        user=self.user,
                        achievement=achievement
                    )
        
        # Find achievements that this completion might trigger
        potential_achievements = Achievement.objects.filter(
            category=self.quest.category,
            required_count__lte=category_count,
            is_active=True
        )
        
        for achievement in potential_achievements:
            # Check if user already has this achievement
            if not UserAchievement.objects.filter(user=self.user, achievement=achievement).exists():
                # Create new user achievement
                UserAchievement.objects.create(
                    user=self.user,
                    achievement=achievement
                )
    
    class Meta:
        unique_together = ('user', 'quest', 'started_at')

class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=QuestCategory.choices,
        null=True, blank=True  # Some achievements may not be category-specific
    )
    # Change CharField to ImageField
    badge_image = models.ImageField(upload_to='achievement_badges/', null=True, blank=True)
    required_count = models.IntegerField(default=1)  # How many quests/actions needed
    points = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')

class Reward(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    partner_name = models.CharField(max_length=100, null=True, blank=True)
    code_template = models.CharField(max_length=255, null=True, blank=True)
    # Change CharField to ImageField
    image = models.ImageField(upload_to='reward_images/', null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class UserReward(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    redemption_code = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.title}"

class UserPoints(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    current_points = models.IntegerField(default=0)  # Points available to spend
    last_updated = models.DateTimeField(auto_now=True)
    
    def add_points(self, points):
        self.total_points += points
        self.current_points += points
        self.save()
        
    def spend_points(self, points):
        if self.current_points >= points:
            self.current_points -= points
            self.save()
            return True
        return False