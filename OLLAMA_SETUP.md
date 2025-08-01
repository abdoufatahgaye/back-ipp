# Configuration Ollama pour le Chatbot BTP Connect

Ce guide explique comment installer et configurer Ollama avec le modèle Gemma2:1b pour le chatbot de BTP Connect.

## Installation d'Ollama

### Windows
1. Téléchargez Ollama depuis le site officiel : https://ollama.ai/download
2. Exécutez l'installateur et suivez les instructions
3. Ollama sera automatiquement démarré en tant que service

### Linux/macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Installation du modèle Gemma2:1b

Une fois Ollama installé, téléchargez le modèle Gemma2:1b :

```bash
ollama pull gemma2:1b
```

## Vérification de l'installation

Pour vérifier que tout fonctionne correctement :

```bash
# Lister les modèles installés
ollama list

# Tester le modèle
ollama run gemma2:1b "Bonjour, comment allez-vous ?"
```

## Configuration dans Django

Les paramètres Ollama sont configurés dans `settings.py` :

```python
# Configuration Ollama
OLLAMA_BASE_URL = 'http://localhost:11434'  # URL par défaut d'Ollama
OLLAMA_MODEL = 'gemma2:1b'                  # Modèle à utiliser
OLLAMA_TIMEOUT = 30                         # Timeout en secondes
```

## Test de l'API

Pour tester l'intégration :

1. Démarrez le serveur Django :
```bash
python manage.py runserver
```

2. Testez le statut d'Ollama :
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/chatbot/status/
```

3. Envoyez un message de test :
```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"content":"Bonjour"}' \
     http://localhost:8000/api/chatbot/send/
```

## Dépannage

### Ollama ne démarre pas
- Vérifiez que le port 11434 n'est pas utilisé par un autre service
- Redémarrez le service Ollama :
  - Windows : Redémarrez le service depuis le gestionnaire de services
  - Linux/macOS : `sudo systemctl restart ollama`

### Le modèle ne se charge pas
- Vérifiez l'espace disque disponible (Gemma2:1b fait environ 1.6GB)
- Réinstallez le modèle : `ollama pull gemma2:1b`

### Erreurs de timeout
- Augmentez la valeur `OLLAMA_TIMEOUT` dans settings.py
- Vérifiez les performances de votre machine (CPU/RAM)

## Modèles alternatifs

Si Gemma2:1b ne fonctionne pas bien, vous pouvez essayer d'autres modèles :

```bash
# Modèles plus légers
ollama pull llama3.2:1b
ollama pull phi3:mini

# Modèles plus performants (nécessitent plus de ressources)
ollama pull gemma2:2b
ollama pull llama3.2:3b
```

N'oubliez pas de mettre à jour `OLLAMA_MODEL` dans settings.py après avoir changé de modèle.

## Performance

- **RAM recommandée** : 4GB minimum, 8GB recommandé
- **CPU** : Processeur moderne avec au moins 4 cœurs
- **Stockage** : 5GB d'espace libre pour le modèle et les données

## Sécurité

- Ollama fonctionne en local par défaut (localhost:11434)
- Aucune donnée n'est envoyée vers des serveurs externes
- Les conversations sont stockées localement dans la base de données Django