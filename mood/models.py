# mood/models.py
from django.db import models
from django.conf import settings

class Mood(models.Model):
    """
    Model for tracking user moods.
    """
    MOOD_CHOICES = (
        (1, 'Very Bad'),
        (2, 'Bad'),
        (3, 'Poor'),
        (4, 'Below Average'),
        (5, 'Average'),
        (6, 'Above Average'),
        (7, 'Good'),
        (8, 'Very Good'),
        (9, 'Great'),
        (10, 'Excellent'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='moods')
    score = models.IntegerField(choices=MOOD_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username}'s mood: {self.get_score_display()} on {self.created_at.date()}"