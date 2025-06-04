from django.urls import path, include
from .views import api_root

urlpatterns = [
    path('', api_root, name='api-root'),  # JSON API root at /api/
    path('users/', include('users.urls')),
    path('conversation/', include('conversation.urls')),
    path('journal/', include('journal.urls')),
    path('mood/', include('mood.urls')),
    path('analytics/', include('analytics.urls')),
    path('gamification/', include('gamification.urls')),
    path('community/', include('community.urls')),
]