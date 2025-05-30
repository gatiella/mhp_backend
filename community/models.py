# backend/community/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class DiscussionGroup(models.Model):
    """
    Model for topic-based discussion groups (anxiety, depression, etc.)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    description = models.TextField()
    topic_type = models.CharField(max_length=50)  # anxiety, depression, etc.
    is_moderated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='DiscussionGroupMembership',
        related_name='joined_groups'
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class DiscussionGroupMembership(models.Model):
    """
    Tracks user memberships in discussion groups
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    discussion_group = models.ForeignKey(DiscussionGroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'discussion_group')
    
    def __str__(self):
        return f"{self.user.username} in {self.discussion_group.name}"


class ForumThread(models.Model):
    """
    Model for forum threads within discussion groups
    """
    title = models.CharField(max_length=200)
    discussion_group = models.ForeignKey(
        DiscussionGroup, 
        on_delete=models.CASCADE,
        related_name='threads'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_threads'
    )
    is_anonymous = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
    
    def __str__(self):
        return self.title


class ForumPost(models.Model):
    """
    Model for posts within forum threads
    """
    thread = models.ForeignKey(
        ForumThread, 
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='forum_posts'
    )
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    encouragements = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Encouragement',
        related_name='encouraged_posts'
    )
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Post in {self.thread.title}"


class Encouragement(models.Model):
    """
    Model for tracking encouragements/support given to forum posts
    """
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    encouragement_type = models.CharField(max_length=50, default='support')  # support, helpful, insightful, etc.
    
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f"{self.user.username} encouraged post {self.post.id}"


class CommunityChallenge(models.Model):
    """
    Model for community challenges and group activities
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_challenges'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    challenge_type = models.CharField(max_length=50)  # meditation, journaling, exercise, etc.
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChallengeParticipation',
        related_name='joined_challenges'
    )
    class meta:
        ordering = ['-created_at'] 
    
    def __str__(self):
        return self.title


class ChallengeParticipation(models.Model):
    """
    Model for tracking user participation in challenges
    """
    challenge = models.ForeignKey(CommunityChallenge, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('challenge', 'user')
    
    def __str__(self):
        return f"{self.user.username} in {self.challenge.title}"


class SuccessStory(models.Model):
    """
    Model for user success stories
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='success_stories'
    )
    is_anonymous = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50)  # anxiety, depression, etc.
    encouragements = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='StoryEncouragement',
        related_name='encouraged_stories'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Success stories"
    
    def __str__(self):
        return self.title


class StoryEncouragement(models.Model):
    """
    Model for tracking encouragements given to success stories
    """
    story = models.ForeignKey(SuccessStory, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('story', 'user')
    
    def __str__(self):
        return f"{self.user.username} encouraged story {self.story.id}"