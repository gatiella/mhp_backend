from django.contrib import admin
from .models import (
    DiscussionGroup,
    DiscussionGroupMembership,
    ForumThread,
    ForumPost,
    Encouragement,
    CommunityChallenge,
    ChallengeParticipation,
    SuccessStory,
    StoryEncouragement
)

@admin.register(DiscussionGroup)
class DiscussionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic_type', 'is_moderated', 'created_at')
    search_fields = ('name', 'topic_type')
    list_filter = ('is_moderated', 'topic_type', 'created_at')

@admin.register(DiscussionGroupMembership)
class DiscussionGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'discussion_group', 'joined_at', 'is_anonymous')
    search_fields = ('user__username', 'discussion_group__name')
    list_filter = ('is_anonymous', 'joined_at')

@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'discussion_group', 'created_by', 'is_pinned', 'is_locked', 'created_at')
    search_fields = ('title', 'discussion_group__name', 'created_by__username')
    list_filter = ('is_pinned', 'is_locked', 'created_at')

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at', 'updated_at')
    search_fields = ('thread__title', 'author__username', 'content')
    list_filter = ('created_at', 'updated_at')

@admin.register(Encouragement)
class EncouragementAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'encouragement_type', 'created_at')
    search_fields = ('post__thread__title', 'user__username')
    list_filter = ('encouragement_type', 'created_at')

@admin.register(CommunityChallenge)
class CommunityChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge_type', 'start_date', 'end_date', 'is_active')
    search_fields = ('title', 'challenge_type')
    list_filter = ('challenge_type', 'is_active', 'start_date', 'end_date')

@admin.register(ChallengeParticipation)
class ChallengeParticipationAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'user', 'joined_at', 'completed')
    search_fields = ('challenge__title', 'user__username')
    list_filter = ('completed', 'joined_at')

@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_approved', 'created_at')
    search_fields = ('title', 'author__username', 'category')
    list_filter = ('category', 'is_approved', 'created_at')

@admin.register(StoryEncouragement)
class StoryEncouragementAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'created_at')
    search_fields = ('story__title', 'user__username')
    list_filter = ('created_at',)
