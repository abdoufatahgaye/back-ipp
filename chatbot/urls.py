from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Conversations
    path('conversations/', views.ChatConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', views.ChatConversationDetailView.as_view(), name='conversation-detail'),
    
    # Messages
    path('send/', views.send_message, name='send-message'),
    path('send/<int:conversation_id>/', views.send_message, name='send-message-to-conversation'),
    path('conversations/<int:conversation_id>/messages/', views.conversation_messages, name='conversation-messages'),
    
    # Status
    path('ollama-status/', views.ollama_status, name='ollama-status'),
]