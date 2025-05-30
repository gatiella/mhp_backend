from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Quest,
    UserQuest,
    Achievement,
    UserAchievement,
    Reward,
    UserReward,
    UserPoints
)

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'points', 'difficulty', 'is_active', 'quest_image_preview')
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ['quest_image_preview']
    
    def quest_image_preview(self, obj):
        """Show a preview of the image in admin list view"""
        if obj.image:
            return f'<img src="{obj.image}" width="50" height="50" />'
        return 'No Image'
    
    quest_image_preview.allow_tags = True
    quest_image_preview.short_description = 'Image Preview'

@admin.register(UserQuest)
class UserQuestAdmin(admin.ModelAdmin):
    list_display = ('user', 'quest', 'started_at', 'is_completed')
    list_filter = ('is_completed', 'quest__category')
    search_fields = ('user__username', 'quest__title')
    raw_id_fields = ('user', 'quest')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'required_count', 'points', 'badge_preview')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')
    readonly_fields = ['badge_preview']
    
    def badge_preview(self, obj):
        """Show a preview of the badge image in admin list view"""
        if obj.badge_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: contain;" />',
                obj.badge_image.url
            )
        return 'No Badge'
    
    badge_preview.short_description = 'Badge Preview'

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement__category',)
    search_fields = ('user__username', 'achievement__title')
    raw_id_fields = ('user', 'achievement')

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_required', 'is_active', 'reward_image_preview')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    readonly_fields = ['reward_image_preview']
    
    def reward_image_preview(self, obj):
        """Show a preview of the image in admin list view"""
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return 'No Image'
    
    reward_image_preview.allow_tags = True
    reward_image_preview.short_description = 'Image Preview'

@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'redeemed_at')
    search_fields = ('user__username', 'reward__title')
    raw_id_fields = ('user', 'reward')

@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'current_points')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)