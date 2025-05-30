# backend/community/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiscussionGroupViewSet, ForumThreadViewSet, 
    ForumPostViewSet, EncouragementViewSet,
    CommunityChallengeViewSet, SuccessStoryViewSet,
    StoryEncouragementViewSet
)

router = DefaultRouter()
router.register(r'discussion-groups', DiscussionGroupViewSet, basename='discussiongroup')
router.register(r'forum-threads', ForumThreadViewSet, basename='forumthread')
router.register(r'forum-posts', ForumPostViewSet, basename='forumpost')
router.register(r'encouragements', EncouragementViewSet, basename='encouragement')
router.register(r'challenges', CommunityChallengeViewSet, basename='communitychallenge')
router.register(r'success-stories', SuccessStoryViewSet, basename='successstory')
router.register(r'story-encouragements', StoryEncouragementViewSet, basename='storyencouragement')

urlpatterns = [
    path('', include(router.urls)),
]