from django.db.models import Count, Q
from ..models import Quest, UserQuest

def get_recommended_quests(user, limit=5):
    """
    Get personalized quest recommendations for a user.
    Always returns a Django QuerySet for compatibility with view operations.
    NOTE: This function no longer applies slicing to allow for ordering in the view.
    """
    completed_quests = UserQuest.objects.filter(
        user=user, is_completed=True
    )
    completed_quest_ids = completed_quests.values_list('quest_id', flat=True)
    
    # If user hasn't completed any quests, return easy quests
    if not completed_quests.exists():
        return Quest.objects.filter(
            is_active=True, 
            difficulty__lte=2
        ).exclude(
            id__in=completed_quest_ids
        )
    
    # Get category preferences based on completed quests
    category_counts = completed_quests.values('quest__category').annotate(
        count=Count('quest__category')
    ).order_by('-count')
    
    if category_counts:
        preferred_category = category_counts[0]['quest__category']
        # Get IDs first without slicing
        recommended_ids = list(Quest.objects.filter(
            category=preferred_category, is_active=True
        ).exclude(
            id__in=completed_quest_ids
        ).values_list('id', flat=True))[:3]
        
        if len(recommended_ids) < limit:
            # Get additional IDs without slicing the queryset
            additional_ids = list(Quest.objects.filter(
                is_active=True
            ).exclude(
                id__in=completed_quest_ids
            ).exclude(
                id__in=recommended_ids
            ).values_list('id', flat=True))[:limit - len(recommended_ids)]
            
            final_ids = recommended_ids + additional_ids
        else:
            final_ids = recommended_ids
        
        # Return a queryset filtered by IDs without slicing
        return Quest.objects.filter(id__in=final_ids)
    else:
        # Fallback if no category counts available
        # Return a queryset without slicing
        return Quest.objects.filter(
            is_active=True
        ).exclude(
            id__in=completed_quest_ids
        )