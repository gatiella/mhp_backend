# gamification/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'quests', views.QuestViewSet)
router.register(r'user-quests', views.UserQuestViewSet, basename='user-quest')
router.register(r'achievements', views.AchievementViewSet)
router.register(r'rewards', views.RewardViewSet)
router.register(r'points', views.UserPointsViewSet, basename='points')

urlpatterns = [
    path('', include(router.urls)),    
    path('streak/', views.get_user_streak, name='get_user_streak'),
    path('completed-dates/', views.get_completed_quest_dates, name='get_completed_quest_dates'),
    
]
