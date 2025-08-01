import requests
import json
import time
from typing import Dict, Any, Optional
from django.conf import settings

class OllamaService:
    def __init__(self):
        self.base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = getattr(settings, 'OLLAMA_MODEL', 'gemma3:1b')
        self.timeout = getattr(settings, 'OLLAMA_TIMEOUT', 30)
    
    def is_available(self) -> bool:
        """Vérifie si Ollama est disponible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def generate_response(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Génère une réponse avec Ollama"""
        start_time = time.time()
        
        # Construire le prompt avec contexte BTP Connect
        system_prompt = self._build_system_prompt()
        full_prompt = f"{system_prompt}\n\nUtilisateur: {message}\nAssistant:"
        
        if context:
            full_prompt = f"{system_prompt}\n\nContexte: {context}\n\nUtilisateur: {message}\nAssistant:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = time.time() - start_time
                
                return {
                    'success': True,
                    'response': result.get('response', '').strip(),
                    'processing_time': processing_time,
                    'model': self.model
                }
            else:
                return {
                    'success': False,
                    'error': f"Erreur HTTP {response.status_code}",
                    'processing_time': time.time() - start_time
                }
                
        except requests.Timeout:
            return {
                'success': False,
                'error': "Timeout lors de la génération de la réponse",
                'processing_time': time.time() - start_time
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Erreur de connexion: {str(e)}",
                'processing_time': time.time() - start_time
            }
    
    def _build_system_prompt(self) -> str:
        """Construit le prompt système pour BTP Connect"""
        return """Tu es l'assistant virtuel de BTP Connect, une plateforme de mise en relation entre clients, maîtres d'œuvre et fournisseurs dans le secteur du BTP en Côte d'Ivoire.

Ton rôle:
- Aider les utilisateurs à naviguer sur la plateforme
- Répondre aux questions sur les commandes, livraisons, prix et paiements
- Fournir des informations sur les matériaux de construction
- Assister dans la gestion des projets BTP
- Être courtois, professionnel et utile

Contexte de la plateforme:
- Marketplace de matériaux de construction
- Gestion de projets BTP
- Système de commandes et livraisons
- Paiements sécurisés en FCFA
- Suivi des commandes et facturation

Réponds toujours en français, de manière claire et concise. Si tu ne connais pas une information spécifique, oriente l'utilisateur vers le support ou les sections appropriées de la plateforme."""
    
    def get_fallback_response(self, message: str) -> str:
        """Réponse de secours si Ollama n'est pas disponible"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['commande', 'commander', 'acheter']):
            return "Pour passer une commande, rendez-vous sur la page Marketplace et sélectionnez les matériaux dont vous avez besoin. Vous pouvez ensuite les ajouter à votre panier."
        
        elif any(word in message_lower for word in ['livraison', 'délai', 'transport']):
            return "Les délais de livraison varient selon le fournisseur et le type de matériau. Vous pouvez consulter les délais estimés sur chaque fiche produit."
        
        elif any(word in message_lower for word in ['prix', 'coût', 'tarif', 'montant']):
            return "Les prix sont affichés en FCFA sur chaque produit. Pour des devis personnalisés ou des volumes importants, contactez directement le fournisseur."
        
        elif any(word in message_lower for word in ['paiement', 'payer', 'facture']):
            return "Nous acceptons plusieurs modes de paiement sécurisés. Les détails sont disponibles lors de la finalisation de votre commande."
        
        elif any(word in message_lower for word in ['aide', 'help', 'support', 'assistance']):
            return "Je suis là pour vous aider ! Vous pouvez me poser des questions sur les commandes, les livraisons, les prix, ou naviguer sur la plateforme. Pour une assistance plus détaillée, contactez notre équipe support."
        
        elif any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir']):
            return "Bonjour ! Ravi de vous voir sur BTP Connect. Comment puis-je vous assister aujourd'hui ?"
        
        else:
            return "Je comprends votre question. Pour une assistance plus détaillée, n'hésitez pas à contacter notre équipe support ou à consulter notre section d'aide."