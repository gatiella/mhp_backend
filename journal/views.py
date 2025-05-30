# journal/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Journal
from .serializers import JournalSerializer
from api.permissions import IsOwner

class JournalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing journal entries.
    """
    serializer_class = JournalSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        return Journal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)