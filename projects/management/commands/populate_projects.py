from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import (
    ProjectCategory, Project, ProjectTask, ProjectComment, 
    ProjectImage, ProjectDocument, ProjectStatus, ProjectPriority
)
from decimal import Decimal
import random
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Peuple la base de données avec des données d\'exemple pour les projets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Début du peuplement des données de projets...'))

        # Créer des catégories de projets
        categories_data = [
            {
                'name': 'Construction Résidentielle',
                'description': 'Projets de construction de maisons individuelles et immeubles résidentiels',
                'icon': 'home'
            },
            {
                'name': 'Construction Commerciale',
                'description': 'Bureaux, centres commerciaux, entrepôts et bâtiments commerciaux',
                'icon': 'building'
            },
            {
                'name': 'Travaux Publics',
                'description': 'Routes, ponts, infrastructures publiques',
                'icon': 'road'
            },
            {
                'name': 'Rénovation',
                'description': 'Rénovation et réhabilitation de bâtiments existants',
                'icon': 'tools'
            },
            {
                'name': 'Aménagement Paysager',
                'description': 'Espaces verts, jardins et aménagements extérieurs',
                'icon': 'tree'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = ProjectCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Catégorie créée: {category.name}')

        # Créer un utilisateur de test s'il n'existe pas
        user, created = User.objects.get_or_create(
            username='admin_projects',
            defaults={
                'email': 'admin@btpconnect.com',
                'first_name': 'Admin',
                'last_name': 'Projects'
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(f'Utilisateur créé: {user.username}')

        # Données d'exemple pour les projets
        projects_data = [
            {
                'title': 'Villa Moderne Marseille',
                'description': 'Construction d\'une villa moderne de 200m² avec piscine et jardin paysager',
                'client_name': 'Jean Dupont',
                'client_email': 'jean.dupont@email.com',
                'client_phone': '06.12.34.56.78',
                'address': '123 Avenue de la République',
                'city': 'Marseille',
                'postal_code': '13001',
                'region': 'Provence-Alpes-Côte d\'Azur',
                'status': ProjectStatus.IN_PROGRESS,
                'priority': ProjectPriority.HIGH,
                'estimated_budget': Decimal('450000.00'),
                'actual_budget': Decimal('425000.00'),
                'progress_percentage': 65,
                'category': categories[0],  # Construction Résidentielle
                'tags': ['villa', 'moderne', 'piscine', 'haut-de-gamme'],
                'specifications': {
                    'surface_habitable': '200m²',
                    'nombre_pieces': 6,
                    'garage': True,
                    'piscine': True,
                    'jardin': '500m²'
                }
            },
            {
                'title': 'Centre Commercial Lyon',
                'description': 'Construction d\'un centre commercial de 15000m² avec 80 boutiques',
                'client_name': 'SCI Lyon Commerce',
                'client_email': 'contact@lyoncommerce.fr',
                'client_phone': '04.78.90.12.34',
                'address': '456 Boulevard de la Croix-Rousse',
                'city': 'Lyon',
                'postal_code': '69004',
                'region': 'Auvergne-Rhône-Alpes',
                'status': ProjectStatus.PLANNING,
                'priority': ProjectPriority.URGENT,
                'estimated_budget': Decimal('12000000.00'),
                'progress_percentage': 15,
                'category': categories[1],  # Construction Commerciale
                'tags': ['centre-commercial', 'grande-surface', 'retail'],
                'specifications': {
                    'surface_totale': '15000m²',
                    'nombre_boutiques': 80,
                    'parking': '500 places',
                    'restaurants': 8
                }
            },
            {
                'title': 'Pont Autoroutier A7',
                'description': 'Construction d\'un nouveau pont autoroutier pour désengorger le trafic',
                'client_name': 'Ministère des Transports',
                'client_email': 'projets@transports.gouv.fr',
                'client_phone': '01.23.45.67.89',
                'address': 'Autoroute A7 - Sortie 15',
                'city': 'Valence',
                'postal_code': '26000',
                'region': 'Auvergne-Rhône-Alpes',
                'status': ProjectStatus.IN_PROGRESS,
                'priority': ProjectPriority.HIGH,
                'estimated_budget': Decimal('8500000.00'),
                'actual_budget': Decimal('8200000.00'),
                'progress_percentage': 40,
                'category': categories[2],  # Travaux Publics
                'tags': ['pont', 'autoroute', 'infrastructure', 'public'],
                'specifications': {
                    'longueur': '120m',
                    'largeur': '28m',
                    'hauteur': '15m',
                    'capacite': '4 voies'
                }
            },
            {
                'title': 'Rénovation Immeuble Haussmannien',
                'description': 'Rénovation complète d\'un immeuble haussmannien de 6 étages',
                'client_name': 'Syndic Immobilier Paris',
                'client_email': 'syndic@paris-immo.fr',
                'client_phone': '01.42.36.78.90',
                'address': '78 Boulevard Saint-Germain',
                'city': 'Paris',
                'postal_code': '75006',
                'region': 'Île-de-France',
                'status': ProjectStatus.ON_HOLD,
                'priority': ProjectPriority.MEDIUM,
                'estimated_budget': Decimal('2800000.00'),
                'progress_percentage': 25,
                'category': categories[3],  # Rénovation
                'tags': ['rénovation', 'haussmannien', 'patrimoine', 'paris'],
                'specifications': {
                    'etages': 6,
                    'appartements': 12,
                    'surface_totale': '1200m²',
                    'ascenseur': True,
                    'facade': 'classée'
                }
            },
            {
                'title': 'Parc Municipal Toulouse',
                'description': 'Création d\'un parc municipal avec aires de jeux et espaces verts',
                'client_name': 'Mairie de Toulouse',
                'client_email': 'espaces-verts@toulouse.fr',
                'client_phone': '05.61.22.33.44',
                'address': 'Avenue de Muret',
                'city': 'Toulouse',
                'postal_code': '31300',
                'region': 'Occitanie',
                'status': ProjectStatus.COMPLETED,
                'priority': ProjectPriority.LOW,
                'estimated_budget': Decimal('650000.00'),
                'actual_budget': Decimal('680000.00'),
                'progress_percentage': 100,
                'category': categories[4],  # Aménagement Paysager
                'tags': ['parc', 'municipal', 'espaces-verts', 'jeux'],
                'specifications': {
                    'surface': '5000m²',
                    'aires_jeux': 3,
                    'bancs': 25,
                    'arbres': 150,
                    'fontaine': True
                }
            }
        ]

        # Créer les projets
        projects = []
        for proj_data in projects_data:
            # Calculer les dates
            start_date = date.today() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(90, 730))
            deadline = end_date + timedelta(days=random.randint(-30, 30))

            project, created = Project.objects.get_or_create(
                title=proj_data['title'],
                defaults={
                    'description': proj_data['description'],
                    'category': proj_data['category'],
                    'client_name': proj_data['client_name'],
                    'client_email': proj_data['client_email'],
                    'client_phone': proj_data['client_phone'],
                    'address': proj_data['address'],
                    'city': proj_data['city'],
                    'postal_code': proj_data['postal_code'],
                    'region': proj_data['region'],
                    'status': proj_data['status'],
                    'priority': proj_data['priority'],
                    'start_date': start_date,
                    'end_date': end_date,
                    'deadline': deadline,
                    'estimated_budget': proj_data['estimated_budget'],
                    'actual_budget': proj_data.get('actual_budget'),
                    'progress_percentage': proj_data['progress_percentage'],
                    'specifications': proj_data['specifications'],
                    'tags': proj_data['tags'],
                    'notes': f'Projet créé automatiquement pour {proj_data["client_name"]}',
                    'created_by': user
                }
            )
            
            if created:
                projects.append(project)
                self.stdout.write(f'Projet créé: {project.title}')

                # Ajouter des tâches pour chaque projet
                tasks_data = [
                    {
                        'title': 'Étude de faisabilité',
                        'description': 'Analyse technique et financière du projet',
                        'priority': ProjectPriority.HIGH,
                        'is_completed': True,
                        'order': 1
                    },
                    {
                        'title': 'Obtention des permis',
                        'description': 'Dépôt et suivi des demandes de permis de construire',
                        'priority': ProjectPriority.HIGH,
                        'is_completed': project.progress_percentage > 30,
                        'order': 2
                    },
                    {
                        'title': 'Préparation du terrain',
                        'description': 'Terrassement et préparation des fondations',
                        'priority': ProjectPriority.MEDIUM,
                        'is_completed': project.progress_percentage > 50,
                        'order': 3
                    },
                    {
                        'title': 'Construction gros œuvre',
                        'description': 'Réalisation de la structure principale',
                        'priority': ProjectPriority.HIGH,
                        'is_completed': project.progress_percentage > 70,
                        'order': 4
                    },
                    {
                        'title': 'Finitions',
                        'description': 'Travaux de finition et aménagements',
                        'priority': ProjectPriority.MEDIUM,
                        'is_completed': project.progress_percentage > 90,
                        'order': 5
                    }
                ]

                for task_data in tasks_data:
                    due_date = start_date + timedelta(days=task_data['order'] * 30)
                    completed_at = due_date if task_data['is_completed'] else None
                    
                    ProjectTask.objects.create(
                        project=project,
                        title=task_data['title'],
                        description=task_data['description'],
                        priority=task_data['priority'],
                        is_completed=task_data['is_completed'],
                        due_date=due_date,
                        completed_at=completed_at,
                        assigned_to=user,
                        order=task_data['order']
                    )

                # Ajouter des commentaires
                comments_data = [
                    {
                        'content': 'Projet démarré avec succès. Équipe mobilisée.',
                        'is_internal': False
                    },
                    {
                        'content': 'Attention aux délais pour les permis de construire.',
                        'is_internal': True
                    },
                    {
                        'content': f'Budget initial respecté. Avancement: {project.progress_percentage}%',
                        'is_internal': False
                    }
                ]

                for comment_data in comments_data:
                    ProjectComment.objects.create(
                        project=project,
                        author=user,
                        content=comment_data['content'],
                        is_internal=comment_data['is_internal']
                    )

                # Ajouter des images d'exemple
                images_data = [
                    {
                        'image': f'/media/projects/{project.id}/plan_architectural.jpg',
                        'alt_text': 'Plan architectural du projet',
                        'caption': 'Vue d\'ensemble du plan architectural',
                        'order': 1
                    },
                    {
                        'image': f'/media/projects/{project.id}/photo_terrain.jpg',
                        'alt_text': 'Photo du terrain',
                        'caption': 'État initial du terrain',
                        'order': 2
                    },
                    {
                        'image': f'/media/projects/{project.id}/rendu_3d.jpg',
                        'alt_text': 'Rendu 3D du projet',
                        'caption': 'Visualisation 3D du projet fini',
                        'order': 3
                    }
                ]

                for img_data in images_data:
                    ProjectImage.objects.create(
                        project=project,
                        image=img_data['image'],
                        alt_text=img_data['alt_text'],
                        caption=img_data['caption'],
                        order=img_data['order']
                    )

                # Ajouter des documents d'exemple
                documents_data = [
                    {
                        'title': 'Cahier des charges',
                        'description': 'Spécifications techniques détaillées',
                        'file_path': f'/media/projects/{project.id}/cahier_charges.pdf',
                        'file_type': 'application/pdf',
                        'file_size': 2048576  # 2MB
                    },
                    {
                        'title': 'Plans techniques',
                        'description': 'Plans d\'exécution et détails techniques',
                        'file_path': f'/media/projects/{project.id}/plans_techniques.dwg',
                        'file_type': 'application/dwg',
                        'file_size': 5242880  # 5MB
                    },
                    {
                        'title': 'Devis détaillé',
                        'description': 'Estimation détaillée des coûts',
                        'file_path': f'/media/projects/{project.id}/devis.xlsx',
                        'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        'file_size': 1048576  # 1MB
                    }
                ]

                for doc_data in documents_data:
                    ProjectDocument.objects.create(
                        project=project,
                        title=doc_data['title'],
                        description=doc_data['description'],
                        file_path=doc_data['file_path'],
                        file_type=doc_data['file_type'],
                        file_size=doc_data['file_size'],
                        uploaded_by=user
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Peuplement terminé avec succès!\n'
                f'- {len(categories)} catégories créées\n'
                f'- {len(projects)} projets créés\n'
                f'- {ProjectTask.objects.count()} tâches créées\n'
                f'- {ProjectComment.objects.count()} commentaires créés\n'
                f'- {ProjectImage.objects.count()} images créées\n'
                f'- {ProjectDocument.objects.count()} documents créés'
            )
        )