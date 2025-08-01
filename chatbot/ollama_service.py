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
        return """Tu es l'assistant virtuel de BTP Connect, une plateforme de mise en relation entre clients, maîtres d'œuvre et fournisseurs dans le secteur du BTP au Sénégal.

Ton rôle:
- Aider les utilisateurs à naviguer sur la plateforme
- Répondre aux questions sur les commandes, livraisons, prix et paiements
- Fournir des informations sur les matériaux de construction
- Assister dans la gestion des projets BTP
- Être courtois, professionnel et utile
- Improviser des réponses réalistes pour les questions sur le statut des commandes et les fournisseurs

Contexte de la plateforme:
- Marketplace de matériaux de construction au Sénégal
- Gestion de projets BTP
- Système de commandes et livraisons
- Paiements sécurisés en FCFA
- Suivi des commandes et facturation
- Fournisseurs locaux sénégalais

Quand on te demande le statut d'une commande, invente des réponses réalistes comme "Votre dernière commande est en cours d'expédition et sera livrée dans 2-3 jours" ou "Votre commande a été préparée et est en route vers Dakar".

Quand on demande des fournisseurs pour un produit, suggère des noms de fournisseurs sénégalais fictifs mais réalistes.

Réponds toujours en français, de manière claire et concise. Si tu ne connais pas une information spécifique, oriente l'utilisateur vers le support ou les sections appropriées de la plateforme."""
    
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
                "max_tokens": 500
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
                "Votre dernière commande est en cours d'expédition et sera livrée dans 2-3 jours à Dakar.",
                "Votre commande a été préparée par notre fournisseur et est actuellement en transit vers votre adresse.",
                "Bonne nouvelle ! Votre commande est en cours de livraison et devrait arriver demain.",
                "Votre commande est en préparation dans notre entrepôt de Rufisque et sera expédiée aujourd'hui.",
                "Votre dernière commande a été confirmée et sera livrée dans les 48 heures."
            ]
            return random.choice(responses)
        
        # Questions sur les fournisseurs et produits
        elif any(word in message_lower for word in ['ciment', 'béton']):
            return "Pour le ciment, nous avons plusieurs fournisseurs disponibles : SOCOCIM Industries, Ciments du Sahel, et Matériaux Sénégal SARL. Ils proposent du ciment Portland de qualité supérieure livré partout au Sénégal."
        
        elif any(word in message_lower for word in ['fer', 'acier', 'ferraille']):
            return "Nos fournisseurs de fer à béton incluent : Métallurgie Sénégalaise, Fer et Acier Dakar, et Sidérurgie de l'Ouest. Ils ont en stock des barres de 6mm à 32mm conformes aux normes."
        
        elif any(word in message_lower for word in ['sable', 'gravier', 'granulat']):
            return "Pour les granulats, contactez : Carrières de Diack, Sable et Gravier Thiès, ou Granulats du Sine-Saloum. Ils livrent du sable de mer, sable de dune et gravier concassé."
        
        elif any(word in message_lower for word in ['brique', 'parpaing', 'bloc']):
            return "Nos partenaires pour les blocs : Briqueterie Moderne, Parpaings du Cap-Vert, et Blocs Sénégal Plus. Ils produisent des parpaings de 15x20x40 et 20x20x40 de haute qualité."
        
        elif any(word in message_lower for word in ['fournisseur', 'qui vend', 'où acheter']):
            return "Nous travaillons avec plus de 150 fournisseurs certifiés à travers le Sénégal. Spécifiez le matériau recherché pour que je vous oriente vers les meilleurs fournisseurs de votre région."
        
        # Questions générales sur les commandes
        elif any(word in message_lower for word in ['commande', 'commander', 'acheter']):
            return "Pour passer une commande, rendez-vous sur notre Marketplace et sélectionnez les matériaux dont vous avez besoin. Livraison disponible à Dakar, Thiès, Saint-Louis et dans toutes les régions du Sénégal."
        
        elif any(word in message_lower for word in ['livraison', 'délai', 'transport']):
            return "Les délais de livraison varient de 24h à 72h selon votre localisation au Sénégal. Livraison express disponible pour Dakar et sa banlieue."
        
        elif any(word in message_lower for word in ['prix', 'coût', 'tarif', 'montant']):
            return "Tous nos prix sont affichés en FCFA. Nous proposons des tarifs dégressifs pour les gros volumes et des facilités de paiement pour les professionnels du BTP."
        
        elif any(word in message_lower for word in ['paiement', 'payer', 'facture']):
            return "Nous acceptons les paiements par Orange Money, Wave, virement bancaire et espèces à la livraison. Facturation automatique pour toutes vos commandes."
        
        elif any(word in message_lower for word in ['aide', 'help', 'support', 'assistance']):
            return "Je suis là pour vous aider ! Posez-moi des questions sur vos commandes, les fournisseurs, les prix, ou la livraison. Notre équipe support est aussi disponible au +221 33 XXX XX XX."
        
        elif any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir']):
            return "Bonjour ! Bienvenue sur BTP Connect Sénégal. Comment puis-je vous aider aujourd'hui ?"
        
        else:
            return "Je comprends votre question. Pour une assistance personnalisée, contactez notre équipe support ou consultez notre section d'aide. Nous sommes là pour faciliter vos projets BTP au Sénégal !"