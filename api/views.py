from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from django.shortcuts import render

# Beautiful landing page view
def landing_page(request):
    return render(request, 'landing.html')

# API root that only returns JSON (no browsable API)
@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])  # Only JSON, no HTML
def api_root(request):
    return Response({
        'message': 'Mental Health Partner API',
        'version': '1.0',
        'endpoints': {
            'users': '/api/users/',
            'conversation': '/api/conversation/',
            'journal': '/api/journal/',
            'mood': '/api/mood/',
            'analytics': '/api/analytics/',
            'gamification': '/api/gamification/',
            'community': '/api/community/'
        },
        'documentation': 'Contact admin for API documentation'
    })

# Optional: Create a browsable API root at a different endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def api_browse(request):
    """Browsable API root - only use if templates are working"""
    return Response({
        'message': 'Mental Health Partner API - Browsable Version',
        'endpoints': {
            'users': '/api/users/',
            'conversation': '/api/conversation/',
            'journal': '/api/journal/',
            'mood': '/api/mood/',
            'analytics': '/api/analytics/',
            'gamification': '/api/gamification/',
            'community': '/api/community/'
        }
    })