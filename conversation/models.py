from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """
    Model for storing conversation sessions.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation with {self.user.username} - {self.title or self.created_at}"

class Message(models.Model):
    """
    Model for storing individual messages within a conversation.
    """
    SENDER_CHOICES = (
        ('user', 'User'),
        ('ai', 'AI'),
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sender = models.CharField(max_length=5, choices=SENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment_score = models.FloatField(null=True, blank=True)  # Optional sentiment analysis
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender} message in {self.conversation}"