#!/usr/bin/env python
"""
Script de diagnostic pour le chatbot
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'btpconnect.settings')
django.setup()

from chatbot.models import ChatConversation, ChatMessage
from chatbot.ollama_service import OllamaService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_database():
    """Test de la base de données"""
    print("\n=== TEST BASE DE DONNÉES ===")
    try:
        # Test de création d'utilisateur
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        print(f"✅ Utilisateur: {user.username} ({'créé' if created else 'existant'})")
        
        # Test de création de conversation
        conversation, created = ChatConversation.objects.get_or_create(
            user=user,
            title='Test Conversation',
            defaults={'is_active': True}
        )
        print(f"✅ Conversation: {conversation.id} ({'créée' if created else 'existante'})")
        
        # Test de création de message
        message = ChatMessage.objects.create(
            conversation=conversation,
            sender='user',
            content='Test message'
        )
        print(f"✅ Message créé: {message.id}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def test_ollama_service():
    """Test du service Ollama"""
    print("\n=== TEST SERVICE OLLAMA ===")
    try:
        service = OllamaService()
        
        # Test de disponibilité
        is_available = service.is_available()
        print(f"{'✅' if is_available else '❌'} Ollama disponible: {is_available}")
        
        if is_available:
            # Test de génération de réponse
            result = service.generate_response("Bonjour, comment allez-vous?")
            print(f"{'✅' if result['success'] else '❌'} Génération réponse: {result['success']}")
            if result['success']:
                print(f"   Réponse: {result['response'][:100]}...")
                print(f"   Temps: {result['processing_time']:.2f}s")
            else:
                print(f"   Erreur: {result['error']}")
        
        return is_available
    except Exception as e:
        print(f"❌ Erreur service Ollama: {e}")
        return False

def test_api_endpoints():
    """Test des endpoints API"""
    print("\n=== TEST ENDPOINTS API ===")
    base_url = "http://127.0.0.1:8000/api/chatbot"
    
    try:
        # Test endpoint status
        response = requests.get(f"{base_url}/ollama-status/")
        print(f"{'✅' if response.status_code == 200 else '❌'} Status endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Ollama disponible: {data.get('ollama_available')}")
            print(f"   Modèle: {data.get('model')}")
        
        # Test endpoint conversations (nécessite authentification)
        response = requests.get(f"{base_url}/conversations/")
        print(f"{'✅' if response.status_code in [200, 401] else '❌'} Conversations endpoint: {response.status_code}")
        
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Django")
        return False
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

def test_streaming():
    """Test du streaming"""
    print("\n=== TEST STREAMING ===")
    try:
        service = OllamaService()
        if service.is_available():
            result = service.generate_response_stream("Test streaming")
            print(f"{'✅' if result['success'] else '❌'} Streaming setup: {result['success']}")
            
            if result['success']:
                chunks = list(result['stream'])
                print(f"   Chunks reçus: {len(chunks)}")
                if chunks:
                    print(f"   Premier chunk: {chunks[0][:50]}...")
        else:
            print("❌ Ollama non disponible pour le streaming")
        
        return True
    except Exception as e:
        print(f"❌ Erreur streaming: {e}")
        return False

def main():
    print(f"DIAGNOSTIC CHATBOT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Tests
    db_ok = test_database()
    ollama_ok = test_ollama_service()
    api_ok = test_api_endpoints()
    streaming_ok = test_streaming()
    
    # Résumé
    print("\n=== RÉSUMÉ ===")
    print(f"Base de données: {'✅' if db_ok else '❌'}")
    print(f"Service Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"API endpoints: {'✅' if api_ok else '❌'}")
    print(f"Streaming: {'✅' if streaming_ok else '❌'}")
    
    if all([db_ok, ollama_ok, api_ok, streaming_ok]):
        print("\n🎉 TOUS LES TESTS PASSENT - Le chatbot devrait fonctionner!")
    else:
        print("\n⚠️  PROBLÈMES DÉTECTÉS - Vérifiez les erreurs ci-dessus")

if __name__ == '__main__':
    main()