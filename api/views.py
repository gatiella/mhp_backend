from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import render

# Beautiful landing page view
def landing_page(request):
    return render(request, 'landing.html')

# Keep your existing API root for /api/browse/ or similar
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'message': 'Mental Health Partner API',
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