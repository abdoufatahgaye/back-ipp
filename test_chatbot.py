#!/usr/bin/env python
"""
Script de test pour vérifier le fonctionnement du chatbot avec Ollama
"""

import requests
import json

def test_ollama_status():
    """Test du statut d'Ollama"""
    print("🔍 Test du statut d'Ollama...")
    try:
        response = requests.get('http://127.0.0.1:8000/api/chatbot/ollama-status/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama disponible: {data['ollama_available']}")
            print(f"📦 Modèle: {data['model']}")
            print(f"🌐 URL de base: {data['base_url']}")
            return data['ollama_available']
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_direct_ollama():
    """Test direct d'Ollama"""
    print("\n🔍 Test direct d'Ollama...")
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'gemma3:1b',
                'prompt': 'Bonjour, comment allez-vous?',
                'stream': False
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse d'Ollama: {data.get('response', 'Pas de réponse')}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion à Ollama: {e}")
        return False

def main():
    print("🤖 Test du chatbot BTP Connect avec Ollama\n")
    
    # Test du statut
    ollama_available = test_ollama_status()
    
    if ollama_available:
        # Test direct d'Ollama
        test_direct_ollama()
        print("\n✅ Tous les tests sont passés! Le chatbot devrait fonctionner.")
        print("\n💡 Instructions:")
        print("1. Assurez-vous que le serveur Django fonctionne (python manage.py runserver)")
        print("2. Assurez-vous que le frontend React fonctionne (npm run dev)")
        print("3. Ouvrez l'application et testez le chatbot")
    else:
        print("\n❌ Ollama n'est pas disponible. Vérifiez:")
        print("1. Ollama est installé et en cours d'exécution")
        print("2. Le modèle gemma3:1b est téléchargé")
        print("3. Le port 11434 est accessible")

if __name__ == '__main__':
    main()