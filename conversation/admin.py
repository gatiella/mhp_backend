from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'created_at', 'sentiment_score')
    list_filter = ('sender', 'created_at')
    search_fields = ('content', 'conversation__title')
    date_hierarchy = 'created_at'
    raw_id_fields = ('conversation',)
