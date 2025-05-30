# journal/models.py
from django.db import models
from django.conf import settings

class Journal(models.Model):
    """
    Model for storing journal entries.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='journal_entries')
    title = models.CharField(max_length=255)
    content = models.TextField()
    mood_score = models.IntegerField(null=True, blank=True)  # Scale 1-10
    mood_note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username}'s journal: {self.title}"