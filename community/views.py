# backend/community/views.py
from django.db.models import Count
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import (
    DiscussionGroup, ForumThread, ForumPost, Encouragement,
    CommunityChallenge, SuccessStory, StoryEncouragement,
    DiscussionGroupMembership, ChallengeParticipation
)
from .serializers import (
    DiscussionGroupSerializer, ForumThreadListSerializer,
    ForumThreadDetailSerializer, ForumPostSerializer,
    EncouragementSerializer, CommunityChallengeSerializer,
    SuccessStorySerializer, StoryEncouragementSerializer
)
from .services.moderation_service import check_content
from api.permissions import IsOwner


class DiscussionGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for discussion groups
    """
    queryset = DiscussionGroup.objects.all()
    serializer_class = DiscussionGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = DiscussionGroup.objects.all()
        topic = self.request.query_params.get('topic', None)
        if topic:
            queryset = queryset.filter(topic_type=topic)
        return queryset
    
    @action(detail=True, methods=['post'])
    def join(self, request, slug=None):
        discussion_group = self.get_object()
        is_anonymous = request.data.get('is_anonymous', False)
        
        if DiscussionGroupMembership.objects.filter(
            user=request.user,
            discussion_group=discussion_group
        ).exists():
            return Response(
                {"detail": "Already a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        DiscussionGroupMembership.objects.create(
            user=request.user,
            discussion_group=discussion_group,
            is_anonymous=is_anonymous
        )
        
        return Response(
            {"detail": "Successfully joined the group."},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, slug=None):
        discussion_group = self.get_object()
        
        membership = DiscussionGroupMembership.objects.filter(
            user=request.user,
            discussion_group=discussion_group
        )
        
        if not membership.exists():
            return Response(
                {"detail": "Not a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership.delete()
        return Response(
            {"detail": "Successfully left the group."},
            status=status.HTTP_200_OK
        )


class ForumThreadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for forum threads
    """
    queryset = ForumThread.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ForumThreadDetailSerializer
        return ForumThreadListSerializer
    
    def get_queryset(self):
        queryset = ForumThread.objects.all()
        group_param = self.request.query_params.get('group', None)

        if group_param:
            queryset = queryset.filter(discussion_group__slug=group_param)

        return queryset.annotate(post_count=Count('posts'))

    
    def perform_create(self, serializer):
        # Check if user is a member of the discussion group
        discussion_group_id = self.request.data.get('discussion_group')
        is_member = DiscussionGroupMembership.objects.filter(
            user=self.request.user,
            discussion_group_id=discussion_group_id
        ).exists()
        
        if not is_member:
            raise PermissionDenied("You must be a member of the group to create a thread.")
        
        # Moderation check
        title = self.request.data.get('title', '')
        if not check_content(title):
            raise PermissionDenied("Content failed moderation check.")
        
        serializer.save(created_by=self.request.user)


class ForumPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for forum posts
    """
    queryset = ForumPost.objects.all()
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ForumPost.objects.all()
        thread_id = self.request.query_params.get('thread', None)
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        return queryset
    
    def perform_create(self, serializer):
        # Check if user is a member of the discussion group
        thread_id = self.request.data.get('thread')
        thread = ForumThread.objects.get(id=thread_id)
        
        is_member = DiscussionGroupMembership.objects.filter(
            user=self.request.user,
            discussion_group=thread.discussion_group
        ).exists()
        
        if not is_member:
            raise PermissionDenied("You must be a member of the group to post.")
        
        if thread.is_locked:
            raise PermissionDenied("This thread is locked.")
        
        # Moderation check
        content = self.request.data.get('content', '')
        if not check_content(content):
            raise PermissionDenied("Content failed moderation check.")
        
        serializer.save(author=self.request.user)


class EncouragementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for post encouragements
    """
    queryset = Encouragement.objects.all()
    serializer_class = EncouragementSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    
    def get_queryset(self):
        return Encouragement.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        post_id = request.data.get('post')
        encouragement_type = request.data.get('encouragement_type', 'support')
        
        # Check if encouragement already exists
        try:
            encouragement = Encouragement.objects.get(
                post_id=post_id,
                user=request.user
            )
            # If exists, remove it (toggle off)
            encouragement.delete()
            return Response(
                {"detail": "Encouragement removed."},
                status=status.HTTP_200_OK
            )
        except Encouragement.DoesNotExist:
            # If doesn't exist, create it (toggle on)
            encouragement = Encouragement.objects.create(
                post_id=post_id,
                user=request.user,
                encouragement_type=encouragement_type
            )
            serializer = self.get_serializer(encouragement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommunityChallengeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for community challenges
    """
    queryset = CommunityChallenge.objects.filter(is_active=True)
    serializer_class = CommunityChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = CommunityChallenge.objects.filter(is_active=True)
        challenge_type = self.request.query_params.get('type', None)
        if challenge_type:
            queryset = queryset.filter(challenge_type=challenge_type)
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        challenge = self.get_object()
        
        if ChallengeParticipation.objects.filter(
            user=request.user,
            challenge=challenge
        ).exists():
            return Response(
                {"detail": "Already participating in this challenge."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ChallengeParticipation.objects.create(
            user=request.user,
            challenge=challenge
        )
        
        return Response(
            {"detail": "Successfully joined the challenge."},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        challenge = self.get_object()
        
        try:
            participation = ChallengeParticipation.objects.get(
                user=request.user,
                challenge=challenge
            )
        except ChallengeParticipation.DoesNotExist:
            return Response(
                {"detail": "Not participating in this challenge."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participation.completed = True
        participation.save()
        
        return Response(
            {"detail": "Challenge marked as completed."},
            status=status.HTTP_200_OK
        )


class SuccessStoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for success stories
    """
    queryset = SuccessStory.objects.filter(is_approved=True)
    serializer_class = SuccessStorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = SuccessStory.objects.filter(is_approved=True)
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset
    
    def perform_create(self, serializer):
        # Moderation check for content
        content = self.request.data.get('content', '')
        if not check_content(content):
            raise PermissionDenied("Content failed moderation check.")
        
        serializer.save(
            author=self.request.user,
            is_approved=False  # All stories require approval
        )


class StoryEncouragementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for story encouragements
    """
    queryset = StoryEncouragement.objects.all()
    serializer_class = StoryEncouragementSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        story_id = request.data.get('story')
        
        # Check if encouragement already exists
        try:
            encouragement = StoryEncouragement.objects.get(
                story_id=story_id,
                user=request.user
            )
            # If exists, remove it (toggle off)
            encouragement.delete()
            return Response(
                {"detail": "Encouragement removed."},
                status=status.HTTP_200_OK
            )
        except StoryEncouragement.DoesNotExist:
            # If doesn't exist, create it (toggle on)
            encouragement = StoryEncouragement.objects.create(
                story_id=story_id,
                user=request.user
            )
            serializer = self.get_serializer(encouragement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)