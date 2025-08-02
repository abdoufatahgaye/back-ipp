from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Supplier, Product
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Peuple la base de données avec des produits d\'exemple'

    def handle(self, *args, **options):
        self.stdout.write('Création des données d\'exemple...')

        # Créer des catégories
        categories_data = [
            {'name': 'Béton & Mortier', 'description': 'Bétons prêts à l\'emploi et mortiers'},
            {'name': 'Acier & Fer', 'description': 'Armatures et structures métalliques'},
            {'name': 'Bois', 'description': 'Bois de construction et charpente'},
            {'name': 'Isolation', 'description': 'Matériaux d\'isolation thermique et phonique'},
            {'name': 'Toiture', 'description': 'Tuiles, ardoises et matériaux de couverture'},
            {'name': 'Granulats', 'description': 'Sables, graviers et granulats'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Catégorie créée: {category.name}')

        # Créer des utilisateurs pour les fournisseurs s'ils n'existent pas
        suppliers_data = [
            {
                'username': 'beton_francilien',
                'email': 'contact@betonfrancilien.fr',
                'company_name': 'Béton Francilien',
                'location': 'Île-de-France',
                'phone': '+33 1 45 67 89 01',
                'description': 'Spécialiste du béton prêt à l\'emploi depuis plus de 20 ans',
                'rating': 4.8,
                'certifications': ['NF EN 206', 'CE', 'ISO 9001']
            },
            {
                'username': 'acier_pro',
                'email': 'ventes@acierpro.fr',
                'company_name': 'Acier Pro',
                'location': 'Rhône-Alpes',
                'phone': '+33 4 76 54 32 10',
                'description': 'Distributeur d\'aciers pour le BTP',
                'rating': 4.6,
                'certifications': ['NF A 35-080', 'CE', 'ISO 14001']
            },
            {
                'username': 'bois_construction',
                'email': 'contact@boisconstruction.fr',
                'company_name': 'Bois Construction',
                'location': 'Nouvelle-Aquitaine',
                'phone': '+33 5 56 78 90 12',
                'description': 'Spécialiste du bois de construction',
                'rating': 4.9,
                'certifications': ['PEFC', 'CE', 'ISO 14001']
            },
            {
                'username': 'iso_materiaux',
                'email': 'ventes@isomateriaux.fr',
                'company_name': 'Iso Matériaux',
                'location': 'Occitanie',
                'phone': '+33 4 67 89 01 23',
                'description': 'Expert en isolation thermique et phonique',
                'rating': 4.7,
                'certifications': ['ACERMI', 'CE', 'ISO 9001']
            },
            {
                'username': 'toiture_excellence',
                'email': 'contact@toitureexcellence.fr',
                'company_name': 'Toiture Excellence',
                'location': 'Provence-Alpes-Côte d\'Azur',
                'phone': '+33 4 94 12 34 56',
                'description': 'Fabricant de tuiles en terre cuite depuis 1950',
                'rating': 4.5,
                'certifications': ['NF', 'CE', 'ISO 14001']
            },
            {
                'username': 'granulats_centre',
                'email': 'commandes@granulatcentre.fr',
                'company_name': 'Granulats Centre',
                'location': 'Centre-Val de Loire',
                'phone': '+33 2 38 45 67 89',
                'description': 'Producteur de granulats depuis 30 ans',
                'rating': 4.4,
                'certifications': ['NF', 'CE', 'ISO 9001']
            }
        ]

        suppliers = {}
        for sup_data in suppliers_data:
            # Créer l'utilisateur s'il n'existe pas
            user, user_created = User.objects.get_or_create(
                username=sup_data['username'],
                defaults={
                    'email': sup_data['email'],
                    'first_name': sup_data['company_name'].split()[0],
                    'last_name': sup_data['company_name'].split()[-1] if len(sup_data['company_name'].split()) > 1 else '',
                }
            )
            
            # Créer le fournisseur
            supplier, created = Supplier.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': sup_data['company_name'],
                    'location': sup_data['location'],
                    'phone': sup_data['phone'],
                    'email': sup_data['email'],
                    'description': sup_data['description'],
                    'rating': sup_data['rating'],
                    'certifications': sup_data['certifications']
                }
            )
            suppliers[sup_data['company_name']] = supplier
            if created:
                self.stdout.write(f'Fournisseur créé: {supplier.company_name}')

        # Créer des produits
        products_data = [
            {
                'id': '1',
                'name': 'Béton C25/30',
                'category': 'Béton & Mortier',
                'supplier': 'Béton Francilien',
                'price': 12500,
                'unit': 'm³',
                'description': 'Béton de qualité C25/30 conforme aux normes européennes.',
                'specifications': {
                    'Classe de résistance': 'C25/30',
                    'Classe d\'exposition': 'XC1, XC2',
                    'Consistance': 'S3 (fluide)',
                    'Dimension max granulats': '20 mm',
                    'Teneur en chlorures': 'Cl 0,20',
                    'Temps de prise': '2-4 heures'
                },
                'image': '/béton.png',
                'images': ['/beton 1.png', '/beton 2.png', '/beton 3.png'],
                'delivery_time': '24-48h',
                'min_order': 3
            },
            {
                'id': '2',
                'name': 'Fer à béton HA12',
                'category': 'Acier & Fer',
                'supplier': 'Acier Pro',
                'price': 285000,
                'unit': 'tonne',
                'description': 'Barres d\'armature haute adhérence HA12 en acier B500B.',
                'specifications': {
                    'Diamètre': '12 mm',
                    'Nuance': 'B500B',
                    'Limite élastique': '500 MPa',
                    'Résistance à la traction': '550 MPa',
                    'Longueur standard': '12 m',
                    'Poids linéique': '0,888 kg/m'
                },
                'image': '/fer à beton.png',
                'images': ['/fer à beton.png', '/fer à beton.png', '/fer à beton.png'],
                'delivery_time': '3-5 jours',
                'min_order': 1
            },
            {
                'id': '3',
                'name': 'Poutre Lamellé-Collé',
                'category': 'Bois',
                'supplier': 'Bois Construction',
                'price': 150000,
                'unit': 'm³',
                'description': 'Poutres en bois lamellé-collé de haute qualité.',
                'specifications': {
                    'Essence': 'Épicéa',
                    'Classe de résistance': 'GL24h',
                    'Humidité': '12% ± 2%',
                    'Dimensions standard': '200x400 mm',
                    'Longueur max': '18 m',
                    'Traitement': 'Classe 2'
                },
                'image': '/poutre lamellé collé.png',
                'images': ['/poutre lamellé collé.png', '/poutre lamellé collé.png', '/poutre lamellé collé.png'],
                'delivery_time': '5-7 jours',
                'min_order': 5
            },
            {
                'id': '4',
                'name': 'Isolant Polyuréthane',
                'category': 'Isolation',
                'supplier': 'Iso Matériaux',
                'price': 4000,
                'unit': 'm²',
                'description': 'Panneaux d\'isolation en polyuréthane haute performance.',
                'specifications': {
                    'Conductivité thermique': '0,022 W/m.K',
                    'Épaisseur': '100 mm',
                    'Dimensions': '1200x600 mm',
                    'Résistance thermique': '4,55 m².K/W',
                    'Réaction au feu': 'E',
                    'Compressibilité': '≤ 10%'
                },
                'image': '/isolant .png',
                'images': ['/isolant .png', '/isolant .png', '/isolant .png'],
                'delivery_time': '7-10 jours',
                'min_order': 10,
                'in_stock': False
            },
            {
                'id': '5',
                'name': 'Tuiles Terre Cuite',
                'category': 'Toiture',
                'supplier': 'Toiture Excellence',
                'price': 12000,
                'unit': 'm²',
                'description': 'Tuiles en terre cuite traditionnelles, résistantes aux intempéries.',
                'specifications': {
                    'Type': 'Tuile canal',
                    'Couleur': 'Rouge naturel',
                    'Dimensions': '400x150 mm',
                    'Poids': '2,2 kg/tuile',
                    'Absorption d\'eau': '≤ 12%',
                    'Résistance au gel': 'Classe 1'
                },
                'image': '/tuiles.png',
                'images': ['/tuiles.png', '/tuiles.png', '/tuiles.png'],
                'delivery_time': '2-4 jours',
                'min_order': 20
            },
            {
                'id': '6',
                'name': 'Sable 0/4',
                'category': 'Granulats',
                'supplier': 'Granulats Centre',
                'price': 9500,
                'unit': 'tonne',
                'description': 'Sable fin 0/4 de qualité, idéal pour les mortiers.',
                'specifications': {
                    'Granulométrie': '0/4 mm',
                    'Origine': 'Carrière',
                    'Propreté': 'SE < 2%',
                    'Équivalent de sable': '> 80%',
                    'Teneur en fines': '< 3%',
                    'Densité': '1,6 t/m³'
                },
                'image': '/sable.png',
                'images': ['/sable.png', '/sable.png', '/sable.png'],
                'delivery_time': '24-48h',
                'min_order': 2
            }
        ]

        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                id=prod_data['id'],
                defaults={
                    'name': prod_data['name'],
                    'category': categories[prod_data['category']],
                    'supplier': suppliers[prod_data['supplier']],
                    'price': prod_data['price'],
                    'unit': prod_data['unit'],
                    'description': prod_data['description'],
                    'specifications': prod_data['specifications'],
                    'image': prod_data['image'],
                    'images': prod_data['images'],
                    'delivery_time': prod_data['delivery_time'],
                    'min_order': prod_data['min_order'],
                    'in_stock': prod_data.get('in_stock', True)
                }
            )
            if created:
                self.stdout.write(f'Produit créé: {product.name}')

        self.stdout.write(
            self.style.SUCCESS('Données d\'exemple créées avec succès!')
        )