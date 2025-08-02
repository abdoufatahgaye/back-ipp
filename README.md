# BATILINK Backend API

## 🏗️ Vue d'ensemble

BATILINK est une plateforme de marketplace BTP qui connecte les clients, maîtres d'œuvre et fournisseurs dans l'écosystème du bâtiment et des travaux publics. Ce backend Django REST Framework fournit une API complète pour gérer les utilisateurs, produits, projets, commandes et communications.

## 🚀 Fonctionnalités principales

### 👥 Gestion des utilisateurs (accounts)
- Authentification JWT avec rotation des tokens
- Trois types d'utilisateurs : CLIENT, MOE (Maître d'œuvre), SUPPLIER (Fournisseur)
- Profils utilisateurs personnalisés
- Gestion des permissions par rôle

### 🛒 Marketplace de produits (products)
- Catalogue de produits BTP avec catégories
- Gestion des fournisseurs et leurs certifications
- Système d'avis et de notation
- Galerie d'images pour chaque produit
- Recherche avancée et filtres
- Recommandations de produits

### 📋 Gestion de projets (projects)
- Création et suivi de projets BTP
- Catégorisation des projets
- Gestion des tâches et sous-tâches
- Système de commentaires
- Upload de documents et images
- Suivi de l'avancement

### 🛍️ Système de commandes (orders)
- Panier d'achat persistant
- Gestion complète des commandes
- Suivi des statuts de commande
- Historique des modifications
- Calcul automatique des frais

### 🤖 Chatbot intelligent (chatbot)
- Assistant IA intégré avec Ollama
- Conversations contextuelles
- Historique des échanges
- Support technique automatisé

## 🛠️ Technologies utilisées

- **Framework** : Django 4.1.4 + Django REST Framework 3.14.0
- **Base de données** : MongoDB avec Djongo
- **Authentification** : JWT avec SimpleJWT
- **IA** : Ollama (Gemma3:1b)
- **Upload de fichiers** : Pillow pour les images
- **CORS** : django-cors-headers
- **Filtres** : django-filter

## 📦 Installation

### Prérequis
- Python 3.8+
- MongoDB (local ou Atlas)
- Ollama (pour le chatbot)

### 1. Cloner le projet
```bash
git clone <repository-url>
cd hackathon-ipp/back
```

### 2. Créer un environnement virtuel
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données
Modifiez `btpconnect/settings.py` avec vos paramètres MongoDB :
```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'votre_db_name',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': "votre_connection_string_mongodb",
        }
    }
}
```

### 5. Configuration d'Ollama (optionnel)
```bash
# Installer Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Télécharger le modèle
ollama pull gemma3:1b

# Démarrer le service
ollama serve
```

### 6. Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur
```bash
python manage.py runserver
```

L'API sera accessible sur `http://localhost:8000/`

## 📚 Structure du projet

```
back/
├── btpconnect/          # Configuration principale Django
│   ├── settings.py      # Paramètres de l'application
│   ├── urls.py         # URLs principales
│   └── wsgi.py         # Configuration WSGI
├── accounts/           # Gestion des utilisateurs
│   ├── models.py       # Modèle User personnalisé
│   ├── serializers.py  # Sérialiseurs pour l'API
│   ├── views.py        # Vues d'authentification
│   └── urls.py         # Routes d'authentification
├── products/           # Marketplace de produits
│   ├── models.py       # Produits, catégories, fournisseurs
│   ├── serializers.py  # Sérialiseurs produits
│   ├── views.py        # API produits
│   └── urls.py         # Routes produits
├── projects/           # Gestion de projets
│   ├── models.py       # Projets, tâches, commentaires
│   ├── serializers.py  # Sérialiseurs projets
│   ├── views.py        # API projets
│   └── urls.py         # Routes projets
├── orders/             # Système de commandes
│   ├── models.py       # Panier, commandes, historique
│   ├── serializers.py  # Sérialiseurs commandes
│   ├── views.py        # API commandes
│   └── urls.py         # Routes commandes
├── chatbot/            # Assistant IA
│   ├── models.py       # Conversations, messages
│   ├── ollama_service.py # Service Ollama
│   ├── views.py        # API chatbot
│   └── urls.py         # Routes chatbot
├── requirements.txt    # Dépendances Python
└── manage.py          # Script de gestion Django
```

## 🔗 Endpoints principaux

### Authentification
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/login/` - Connexion
- `GET /api/auth/profile/` - Profil utilisateur
- `PUT /api/auth/profile/` - Mise à jour profil

### Produits
- `GET /api/products/` - Liste des produits
- `POST /api/products/` - Créer un produit
- `GET /api/products/{uuid}/` - Détail produit
- `GET /api/categories/` - Catégories
- `GET /api/suppliers/` - Fournisseurs

### Projets
- `GET /api/projects/` - Liste des projets
- `POST /api/projects/` - Créer un projet
- `GET /api/projects/{uuid}/` - Détail projet
- `GET /api/projects/categories/` - Catégories de projets

### Commandes
- `GET /api/orders/cart/` - Panier actuel
- `POST /api/orders/cart/add/` - Ajouter au panier
- `GET /api/orders/` - Liste des commandes
- `POST /api/orders/` - Créer une commande

### Chatbot
- `GET /api/chatbot/conversations/` - Conversations
- `POST /api/chatbot/conversations/` - Nouvelle conversation
- `POST /api/chatbot/conversations/{id}/messages/` - Envoyer message

## 🔧 Configuration

### Variables d'environnement
Créez un fichier `.env` :
```env
SECRET_KEY=votre_secret_key_django
DEBUG=True
MONGODB_URI=votre_connection_string_mongodb
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:1b
```

### CORS
Le CORS est configuré pour accepter les requêtes depuis :
- `http://localhost:5174` (frontend Vite)
- `http://127.0.0.1:5174`

### JWT
Configuration des tokens JWT :
- **Access Token** : 60 minutes
- **Refresh Token** : 1 jour
- **Rotation** : Activée

## 📖 Documentation API

Une documentation détaillée de l'API est disponible dans `API_DOCUMENTATION.md`.

### Exemples d'utilisation

#### Authentification
```bash
# Connexion
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'

# Utilisation du token
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Recherche de produits
```bash
# Recherche avec filtres
curl "http://localhost:8000/api/products/?search=béton&category=1&min_price=1000"
```

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests d'une application spécifique
python manage.py test products
```

## 📊 Administration

Interface d'administration Django disponible sur `/admin/`

Modèles enregistrés :
- Utilisateurs et profils
- Produits et catégories
- Projets et tâches
- Commandes et paniers
- Conversations chatbot

## 🚀 Déploiement

### Production
1. Configurez `DEBUG = False`
2. Définissez `ALLOWED_HOSTS`
3. Configurez une base de données de production
4. Collectez les fichiers statiques : `python manage.py collectstatic`
5. Utilisez un serveur WSGI comme Gunicorn

### Docker (optionnel)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "btpconnect.wsgi:application"]
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Consultez la documentation API
- Vérifiez les logs Django
- Contactez l'équipe de développement

---

**BATILINK** - Connecter l'écosystème BTP 🏗️