# mood/views.py
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Mood
from .serializers import MoodSerializer
from api.permissions import IsOwner

class MoodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mood records.
    """
    serializer_class = MoodSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        return Mood.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)