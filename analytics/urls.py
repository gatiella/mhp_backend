# analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('mood/', views.MoodAnalyticsView.as_view(), name='mood-analytics'),
    path('activity/', views.UserActivityView.as_view(), name='user-activity'),
]