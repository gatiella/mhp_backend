from django.contrib import admin
from .models import Mood

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_score_display', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'note')
    date_hierarchy = 'created_at'
