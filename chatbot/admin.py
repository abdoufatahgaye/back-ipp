from django.contrib import admin
from .models import ChatConversation, ChatMessage

@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'message_count', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Nombre de messages'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('messages')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'content_preview', 'timestamp', 'is_processed', 'processing_time']
    list_filter = ['sender', 'is_processed', 'timestamp']
    search_fields = ['content', 'conversation__user__username']
    readonly_fields = ['timestamp', 'processing_time']
    date_hierarchy = 'timestamp'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Aperçu du contenu'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation__user')
