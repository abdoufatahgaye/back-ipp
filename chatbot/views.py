from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import ChatConversation, ChatMessage
from .serializers import (
    ChatConversationSerializer, 
    ChatMessageSerializer, 
    ChatMessageCreateSerializer
)
from .ollama_service import OllamaService
import logging

logger = logging.getLogger(__name__)

class ChatConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatConversation.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatConversation.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, conversation_id=None):
    """Envoie un message et génère une réponse du bot"""
    try:
        # Récupérer ou créer une conversation
        if conversation_id:
            conversation = get_object_or_404(
                ChatConversation, 
                id=conversation_id, 
                user=request.user, 
                is_active=True
            )
        else:
            # Créer une nouvelle conversation
            conversation = ChatConversation.objects.create(
                user=request.user,
                title=f"Conversation {timezone.now().strftime('%d/%m/%Y %H:%M')}"
            )
        
        # Valider et sauvegarder le message utilisateur
        message_serializer = ChatMessageCreateSerializer(data=request.data)
        if not message_serializer.is_valid():
            return Response(
                message_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_message = ChatMessage.objects.create(
            conversation=conversation,
            sender='user',
            content=message_serializer.validated_data['content']
        )
        
        # Générer la réponse du bot
        ollama_service = OllamaService()
        
        # Construire le contexte avec les messages précédents
        recent_messages = conversation.messages.order_by('-timestamp')[:5]
        context = "\n".join([
            f"{msg.sender}: {msg.content}" 
            for msg in reversed(recent_messages)
        ])
        
        # Générer la réponse
        if ollama_service.is_available():
            result = ollama_service.generate_response(
                user_message.content, 
                context=context
            )
            
            if result['success']:
                bot_response = result['response']
                processing_time = result['processing_time']
            else:
                logger.warning(f"Erreur Ollama: {result['error']}")
                bot_response = ollama_service.get_fallback_response(user_message.content)
                processing_time = result['processing_time']
        else:
            logger.warning("Ollama non disponible, utilisation des réponses de secours")
            bot_response = ollama_service.get_fallback_response(user_message.content)
            processing_time = 0.1
        
        # Sauvegarder la réponse du bot
        bot_message = ChatMessage.objects.create(
            conversation=conversation,
            sender='bot',
            content=bot_response,
            is_processed=True,
            processing_time=processing_time
        )
        
        # Mettre à jour la conversation
        conversation.updated_at = timezone.now()
        conversation.save()
        
        # Retourner les messages
        return Response({
            'conversation_id': conversation.id,
            'user_message': ChatMessageSerializer(user_message).data,
            'bot_message': ChatMessageSerializer(bot_message).data,
            'processing_time': processing_time
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {str(e)}")
        return Response(
            {'error': 'Une erreur est survenue lors du traitement de votre message.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conversation_id):
    """Récupère tous les messages d'une conversation"""
    conversation = get_object_or_404(
        ChatConversation, 
        id=conversation_id, 
        user=request.user, 
        is_active=True
    )
    
    messages = conversation.messages.all()
    serializer = ChatMessageSerializer(messages, many=True)
    
    return Response({
        'conversation': ChatConversationSerializer(conversation).data,
        'messages': serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def ollama_status(request):
    """Vérifie le statut d'Ollama"""
    ollama_service = OllamaService()
    is_available = ollama_service.is_available()
    
    return Response({
        'ollama_available': is_available,
        'model': ollama_service.model,
        'base_url': ollama_service.base_url
    })
