# Documentation API Produits - BTP Connect

## Vue d'ensemble

Cette API REST permet de gérer un marketplace de produits BTP avec des fonctionnalités CRUD complètes pour les produits, catégories, fournisseurs, avis et images.

## Base URL
```
http://localhost:8000/api/
```

## Authentification

La plupart des endpoints nécessitent une authentification JWT. Incluez le token dans l'en-tête :
```
Authorization: Bearer <votre_token_jwt>
```

## Endpoints Disponibles

### 🏷️ Catégories

#### Lister toutes les catégories
```http
GET /api/categories/
```

#### Créer une catégorie
```http
POST /api/categories/
Content-Type: application/json

{
    "name": "Nouvelle Catégorie",
    "description": "Description de la catégorie"
}
```

#### Détails d'une catégorie
```http
GET /api/categories/{id}/
```

#### Modifier une catégorie
```http
PUT /api/categories/{id}/
PATCH /api/categories/{id}/
```

#### Supprimer une catégorie
```http
DELETE /api/categories/{id}/
```

### 🏢 Fournisseurs

#### Lister tous les fournisseurs
```http
GET /api/suppliers/
```

Paramètres de recherche :
- `search` : Recherche par nom ou localisation
- `ordering` : Tri par `company_name`, `rating`, `created_at`

#### Créer un fournisseur
```http
POST /api/suppliers/
Content-Type: application/json

{
    "company_name": "Ma Société",
    "location": "Paris",
    "phone": "+33 1 23 45 67 89",
    "email": "contact@masociete.fr",
    "description": "Description de l'entreprise",
    "rating": 4.5,
    "certifications": ["NF", "CE"]
}
```

#### Détails d'un fournisseur
```http
GET /api/suppliers/{id}/
```

### 📦 Produits

#### Lister tous les produits
```http
GET /api/products/
```

Paramètres de filtrage :
- `category` : ID de la catégorie
- `supplier` : ID du fournisseur
- `in_stock` : true/false
- `unit` : Unité du produit
- `min_price` : Prix minimum
- `max_price` : Prix maximum
- `category_name` : Nom de la catégorie (recherche)
- `supplier_name` : Nom du fournisseur (recherche)
- `search` : Recherche dans nom, description, fournisseur
- `ordering` : Tri par `name`, `price`, `created_at`

Exemple :
```http
GET /api/products/?category=1&in_stock=true&min_price=1000&ordering=-created_at
```

#### Créer un produit
```http
POST /api/products/
Content-Type: application/json

{
    "name": "Nouveau Produit",
    "category": 1,
    "supplier": 1,
    "price": 15000,
    "unit": "m³",
    "description": "Description du produit",
    "specifications": {
        "Propriété 1": "Valeur 1",
        "Propriété 2": "Valeur 2"
    },
    "image": "/chemin/vers/image.png",
    "images": ["/image1.png", "/image2.png"],
    "in_stock": true,
    "delivery_time": "24-48h",
    "min_order": 1,
    "is_active": true
}
```

#### Détails d'un produit
```http
GET /api/products/{uuid}/
```

#### Modifier un produit
```http
PUT /api/products/{uuid}/
PATCH /api/products/{uuid}/
```

#### Supprimer un produit
```http
DELETE /api/products/{uuid}/
```

#### Recherche avancée de produits
```http
GET /api/products/search/?q=béton
```

#### Recommandations de produits
```http
GET /api/products/{uuid}/recommendations/
```

### ⭐ Avis Produits

#### Lister les avis d'un produit
```http
GET /api/products/{product_uuid}/reviews/
```

#### Créer un avis
```http
POST /api/products/{product_uuid}/reviews/
Content-Type: application/json

{
    "rating": 5,
    "comment": "Excellent produit !"
}
```

#### Modifier/Supprimer un avis
```http
PUT /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

### 🖼️ Images Produits

#### Lister les images d'un produit
```http
GET /api/products/{product_uuid}/images/
```

#### Ajouter une image
```http
POST /api/products/{product_uuid}/images/
Content-Type: multipart/form-data

image: [fichier]
alt_text: "Description de l'image"
order: 1
```

#### Modifier/Supprimer une image
```http
PUT /api/images/{id}/
DELETE /api/images/{id}/
```

### 📊 Statistiques

#### Statistiques générales
```http
GET /api/statistics/
```

Retourne :
- Nombre total de produits
- Nombre de catégories
- Nombre de fournisseurs
- Produits en stock
- Top catégories
- Top fournisseurs

### 🔄 Opérations en lot

#### Mise à jour en lot
```http
POST /api/products/bulk-update/
Content-Type: application/json

{
    "product_ids": ["uuid1", "uuid2"],
    "update_data": {
        "in_stock": false,
        "delivery_time": "5-7 jours"
    }
}
```

#### Suppression en lot
```http
DELETE /api/products/bulk-delete/
Content-Type: application/json

{
    "product_ids": ["uuid1", "uuid2"]
}
```

## Codes de réponse

- `200 OK` : Succès
- `201 Created` : Ressource créée
- `400 Bad Request` : Données invalides
- `401 Unauthorized` : Authentification requise
- `403 Forbidden` : Permissions insuffisantes
- `404 Not Found` : Ressource non trouvée
- `500 Internal Server Error` : Erreur serveur

## Exemples de réponses

### Liste de produits
```json
{
    "count": 6,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "1",
            "name": "Béton C25/30",
            "category_name": "Béton & Mortier",
            "supplier_name": "Béton Francilien",
            "supplier_rating": "4.8",
            "price": "12500.00",
            "unit": "m³",
            "image": "/béton.png",
            "in_stock": true,
            "delivery_time": "24-48h",
            "average_rating": 0.0,
            "reviews_count": 0,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Détail d'un produit
```json
{
    "id": "1",
    "name": "Béton C25/30",
    "category": {
        "id": 1,
        "name": "Béton & Mortier",
        "description": "Bétons prêts à l'emploi et mortiers"
    },
    "supplier": {
        "id": 1,
        "company_name": "Béton Francilien",
        "location": "Île-de-France",
        "rating": "4.8"
    },
    "price": "12500.00",
    "unit": "m³",
    "description": "Béton de qualité C25/30 conforme aux normes européennes.",
    "specifications": {
        "Classe de résistance": "C25/30",
        "Consistance": "S3 (fluide)"
    },
    "image": "/béton.png",
    "images": ["/beton 1.png", "/beton 2.png", "/beton 3.png"],
    "in_stock": true,
    "delivery_time": "24-48h",
    "min_order": 3,
    "reviews": [],
    "average_rating": 0.0,
    "reviews_count": 0
}
```

## Installation et utilisation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Appliquer les migrations :
```bash
python manage.py migrate
```

3. Peupler avec des données d'exemple :
```bash
python manage.py populate_products
```

4. Démarrer le serveur :
```bash
python manage.py runserver
```

L'API sera disponible sur `http://localhost:8000/api/`