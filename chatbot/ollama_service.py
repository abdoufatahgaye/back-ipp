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
                "max_tokens": 150
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    processing_time = time.time() - start_time
                    
                    response_text = result.get('response', '').strip()
                    # Nettoyer la réponse des caractères problématiques
                    response_text = response_text.encode('utf-8', errors='ignore').decode('utf-8')
                    
                    return {
                        'success': True,
                        'response': response_text,
                        'processing_time': processing_time,
                        'model': self.model
                    }
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    return {
                        'success': False,
                        'error': f"Erreur de décodage: {str(e)}",
                        'processing_time': time.time() - start_time
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
        return """Tu es l'assistant virtuel de BTP Connect, plateforme BTP au Sénégal.

IMPORTANT: Réponds TOUJOURS de manière TRÈS COURTE et CONCISE (maximum 2-3 phrases).

Ton rôle: Aider avec les commandes, livraisons, prix, matériaux BTP et projets.

Contexte: Marketplace matériaux construction Sénégal, paiements FCFA, fournisseurs locaux.

Pour les statuts de commandes, invente des réponses courtes et réalistes.
Pour les fournisseurs, suggère des noms sénégalais fictifs.

Réponds en français, sois direct et concis."""
    
    def generate_response_stream(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Génère une réponse en streaming avec Ollama"""
        start_time = time.time()
        
        # Construire le prompt avec contexte BTP Connect
        system_prompt = self._build_system_prompt()
        full_prompt = f"{system_prompt}\n\nUtilisateur: {message}\nAssistant:"
        
        if context:
            full_prompt = f"{system_prompt}\n\nContexte: {context}\n\nUtilisateur: {message}\nAssistant:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 150
            }
        }
        
        def stream_generator():
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout,
                    stream=True
                )
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if 'response' in data:
                                    yield data['response']
                                if data.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    yield f"Erreur HTTP {response.status_code}"
                    
            except Exception as e:
                yield f"Erreur: {str(e)}"
        
        try:
            processing_time = time.time() - start_time
            return {
                'success': True,
                'stream': stream_generator(),
                'processing_time': processing_time,
                'model': self.model
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def get_fallback_response(self, message: str) -> str:
        """Réponse de secours si Ollama n'est pas disponible"""
        message_lower = message.lower()
        
        # Questions sur le statut des commandes
        if any(word in message_lower for word in ['statut', 'état', 'suivi', 'où est', 'dernière commande']):
            import random
            responses = [
                "Votre commande est en cours d'expédition, livraison dans 2-3 jours.",
                "Commande préparée, en transit vers votre adresse.",
                "Votre commande arrive demain !",
                "En préparation à Rufisque, expédition aujourd'hui.",
                "Commande confirmée, livraison sous 48h."
            ]
            return random.choice(responses)
        
        # Questions sur les fournisseurs et produits
        elif any(word in message_lower for word in ['ciment', 'béton']):
            return "Ciment disponible : SOCOCIM Industries, Ciments du Sahel. Livraison partout au Sénégal."
        
        elif any(word in message_lower for word in ['fer', 'acier', 'ferraille']):
            return "Fer à béton : Métallurgie Sénégalaise, Fer et Acier Dakar. Barres 6mm à 32mm en stock."
        
        elif any(word in message_lower for word in ['sable', 'gravier', 'granulat']):
            return "Granulats : Carrières de Diack, Sable et Gravier Thiès. Sable de mer et gravier disponibles."
        
        elif any(word in message_lower for word in ['brique', 'parpaing', 'bloc']):
            return "Parpaings : Briqueterie Moderne, Blocs Sénégal Plus. Formats 15x20x40 et 20x20x40."
        
        elif any(word in message_lower for word in ['fournisseur', 'qui vend', 'où acheter']):
            return "Plus de 150 fournisseurs certifiés. Précisez le matériau recherché."
        
        # Questions générales sur les commandes
        elif any(word in message_lower for word in ['commande', 'commander', 'acheter']):
            return "Commandez sur notre Marketplace. Livraison dans toutes les régions du Sénégal."
        
        elif any(word in message_lower for word in ['livraison', 'délai', 'transport']):
            return "Délais : 24h à 72h selon votre localisation. Express pour Dakar."
        
        elif any(word in message_lower for word in ['prix', 'coût', 'tarif', 'montant']):
            return "Prix en FCFA. Tarifs dégressifs et facilités de paiement disponibles."
        
        elif any(word in message_lower for word in ['paiement', 'payer', 'facture']):
            return "Paiements : Orange Money, Wave, virement, espèces. Facturation automatique."
        
        elif any(word in message_lower for word in ['aide', 'help', 'support', 'assistance']):
            return "Je vous aide avec commandes, fournisseurs, prix et livraisons. Support : +221 33 XXX XX XX."
        
        elif any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir']):
            return "Bonjour ! Bienvenue sur BTP Connect. Comment puis-je vous aider ?"
        
        else:
            return "Pour une assistance personnalisée, contactez notre support ou consultez l'aide."