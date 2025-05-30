# analytics/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from .serializers import MoodAnalyticsSerializer, UserActivitySerializer
from mood.models import Mood
from journal.models import Journal
from conversation.models import Conversation, Message

class MoodAnalyticsView(APIView):
    """
    API view for mood analytics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get the time range from query parameters (default: 7 days)
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get average mood scores grouped by date
        moods = Mood.objects.filter(
            user=request.user,
            created_at__gte=start_date
        ).values('created_at__date').annotate(
            avg_score=Avg('score'),
            count=Count('id')
        ).order_by('created_at__date')
        
        # Format the data for the response
        data = [
            {
                'date': mood['created_at__date'],
                'avg_score': mood['avg_score'],
                'count': mood['count']
            }
            for mood in moods
        ]
        
        return Response(data)

class UserActivityView(APIView):
    """
    API view for user activity analytics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get conversation statistics
        conversations = Conversation.objects.filter(user=request.user)
        conversations_count = conversations.count()
        
        # Get message statistics
        messages = Message.objects.filter(conversation__user=request.user)
        messages_count = messages.count()
        
        # Estimate conversation minutes (rough approximation)
        conversation_minutes = messages_count * 0.5  # Assuming 30 seconds per message
        
        # Get journal statistics
        journals_count = Journal.objects.filter(user=request.user).count()
        
        # Get mood statistics
        moods_count = Mood.objects.filter(user=request.user).count()
        
        # Format the data for the response
        data = {
            'conversations_count': conversations_count,
            'messages_count': messages_count,
            'journals_count': journals_count,
            'moods_count': moods_count,
            'conversation_minutes': conversation_minutes
        }
        
        return Response(data)