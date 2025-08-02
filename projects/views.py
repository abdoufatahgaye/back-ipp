from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    ProjectCategory, Project, ProjectImage, ProjectTask, 
    ProjectComment, ProjectDocument, ProjectStatus, ProjectPriority
)
from .serializers import (
    ProjectCategorySerializer, ProjectListSerializer, ProjectDetailSerializer,
    ProjectCreateUpdateSerializer, ProjectImageSerializer, ProjectTaskSerializer,
    ProjectCommentSerializer, ProjectDocumentSerializer, ProjectStatsSerializer,
    ProjectBulkUpdateSerializer
)


# ==================== CATÉGORIES DE PROJETS ====================

class ProjectCategoryListCreateView(generics.ListCreateAPIView):
    """Liste et création des catégories de projets"""
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProjectCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'une catégorie"""
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [IsAuthenticated]


# ==================== PROJETS ====================

class ProjectFilter(DjangoFilterBackend):
    """Filtres personnalisés pour les projets"""
    class Meta:
        model = Project
        fields = {
            'category': ['exact'],
            'status': ['exact', 'in'],
            'priority': ['exact', 'in'],
            'city': ['exact', 'icontains'],
            'region': ['exact', 'icontains'],
            'created_by': ['exact'],
            'start_date': ['gte', 'lte'],
            'end_date': ['gte', 'lte'],
            'deadline': ['gte', 'lte'],
            'estimated_budget': ['gte', 'lte'],
            'progress_percentage': ['gte', 'lte'],
        }


class ProjectListCreateView(generics.ListCreateAPIView):
    """Liste et création des projets"""
    queryset = Project.objects.select_related('category', 'created_by').prefetch_related('assigned_to')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'category': ['exact'],
        'status': ['exact', 'in'],
        'priority': ['exact', 'in'],
        'city': ['exact', 'icontains'],
        'region': ['exact', 'icontains'],
        'created_by': ['exact'],
        'start_date': ['gte', 'lte'],
        'end_date': ['gte', 'lte'],
        'deadline': ['gte', 'lte'],
        'estimated_budget': ['gte', 'lte'],
        'progress_percentage': ['gte', 'lte'],
    }
    search_fields = ['title', 'description', 'client_name', 'address', 'city']
    ordering_fields = ['title', 'created_at', 'start_date', 'deadline', 'priority', 'progress_percentage']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateUpdateSerializer
        return ProjectListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres personnalisés
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                deadline__lt=today,
                status__in=[ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS]
            )
        
        assigned_to_me = self.request.query_params.get('assigned_to_me')
        if assigned_to_me == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        created_by_me = self.request.query_params.get('created_by_me')
        if created_by_me == 'true':
            queryset = queryset.filter(created_by=self.request.user)
        
        return queryset


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'un projet"""
    queryset = Project.objects.select_related('category', 'created_by').prefetch_related(
        'assigned_to', 'images', 'tasks', 'comments__author', 'documents__uploaded_by'
    )
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_search(request):
    """Recherche avancée de projets"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'results': []})

    projects = Project.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(client_name__icontains=query) |
        Q(address__icontains=query) |
        Q(city__icontains=query) |
        Q(category__name__icontains=query)
    ).select_related('category', 'created_by')[:20]

    serializer = ProjectListSerializer(projects, many=True)
    return Response({'results': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_recommendations(request, project_id):
    """Recommandations de projets similaires"""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({'error': 'Projet non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    # Projets similaires basés sur la catégorie et la localisation
    similar_projects = Project.objects.filter(
        Q(category=project.category) |
        Q(city=project.city) |
        Q(region=project.region)
    ).exclude(id=project.id).select_related('category', 'created_by')[:10]

    serializer = ProjectListSerializer(similar_projects, many=True)
    return Response({'recommendations': serializer.data})


# ==================== TÂCHES DE PROJETS ====================

class ProjectTaskListCreateView(generics.ListCreateAPIView):
    """Liste et création des tâches d'un projet"""
    serializer_class = ProjectTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'due_date', 'priority', 'created_at']
    ordering = ['order', 'created_at']

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectTask.objects.filter(project_id=project_id).select_related('assigned_to')

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(project_id=project_id)


class ProjectTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'une tâche"""
    queryset = ProjectTask.objects.select_related('assigned_to', 'project')
    serializer_class = ProjectTaskSerializer
    permission_classes = [IsAuthenticated]


# ==================== COMMENTAIRES DE PROJETS ====================

class ProjectCommentListCreateView(generics.ListCreateAPIView):
    """Liste et création des commentaires d'un projet"""
    serializer_class = ProjectCommentSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        queryset = ProjectComment.objects.filter(project_id=project_id).select_related('author')
        
        # Filtrer les commentaires internes si l'utilisateur n'est pas staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_internal=False)
        
        return queryset

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(project_id=project_id)


class ProjectCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'un commentaire"""
    queryset = ProjectComment.objects.select_related('author', 'project')
    serializer_class = ProjectCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Seul l'auteur peut modifier/supprimer son commentaire
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            queryset = queryset.filter(author=self.request.user)
        return queryset


# ==================== IMAGES DE PROJETS ====================

class ProjectImageListCreateView(generics.ListCreateAPIView):
    """Liste et ajout d'images pour un projet"""
    serializer_class = ProjectImageSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['order', 'uploaded_at']

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectImage.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(project_id=project_id)


class ProjectImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'une image"""
    queryset = ProjectImage.objects.select_related('project')
    serializer_class = ProjectImageSerializer
    permission_classes = [IsAuthenticated]


# ==================== DOCUMENTS DE PROJETS ====================

class ProjectDocumentListCreateView(generics.ListCreateAPIView):
    """Liste et ajout de documents pour un projet"""
    serializer_class = ProjectDocumentSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-uploaded_at']

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectDocument.objects.filter(project_id=project_id).select_related('uploaded_by')

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(project_id=project_id)


class ProjectDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'un document"""
    queryset = ProjectDocument.objects.select_related('uploaded_by', 'project')
    serializer_class = ProjectDocumentSerializer
    permission_classes = [IsAuthenticated]


# ==================== STATISTIQUES ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_statistics(request):
    """Statistiques générales des projets"""
    # Statistiques de base
    total_projects = Project.objects.count()
    
    # Projets par statut
    projects_by_status = dict(
        Project.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )
    
    # Projets par priorité
    projects_by_priority = dict(
        Project.objects.values('priority').annotate(count=Count('id')).values_list('priority', 'count')
    )
    
    # Projets par catégorie
    projects_by_category = dict(
        Project.objects.select_related('category').values('category__name').annotate(
            count=Count('id')
        ).values_list('category__name', 'count')
    )
    
    # Projets en retard
    today = timezone.now().date()
    overdue_projects = Project.objects.filter(
        deadline__lt=today,
        status__in=[ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS]
    ).count()
    
    # Budget total
    total_budget = Project.objects.aggregate(
        total=Sum('estimated_budget')
    )['total'] or 0
    
    # Progression moyenne
    average_progress = Project.objects.aggregate(
        avg=Avg('progress_percentage')
    )['avg'] or 0
    
    # Projets récents
    recent_projects = Project.objects.select_related('category', 'created_by').order_by('-created_at')[:5]
    
    stats_data = {
        'total_projects': total_projects,
        'projects_by_status': projects_by_status,
        'projects_by_priority': projects_by_priority,
        'projects_by_category': projects_by_category,
        'overdue_projects': overdue_projects,
        'total_budget': total_budget,
        'average_progress': round(average_progress, 2),
        'recent_projects': recent_projects
    }
    
    serializer = ProjectStatsSerializer(stats_data)
    return Response(serializer.data)


# ==================== OPÉRATIONS EN LOT ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_bulk_update(request):
    """Mise à jour en lot des projets"""
    serializer = ProjectBulkUpdateSerializer(data=request.data)
    if serializer.is_valid():
        project_ids = serializer.validated_data['project_ids']
        update_data = serializer.validated_data['update_data']
        
        # Vérifier que l'utilisateur a accès aux projets
        projects = Project.objects.filter(id__in=project_ids)
        if projects.count() != len(project_ids):
            return Response(
                {'error': 'Certains projets sont introuvables'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Effectuer la mise à jour
        updated_count = projects.update(**update_data)
        
        return Response({
            'message': f'{updated_count} projets mis à jour avec succès',
            'updated_count': updated_count
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def project_bulk_delete(request):
    """Suppression en lot des projets"""
    project_ids = request.data.get('project_ids', [])
    
    if not project_ids:
        return Response(
            {'error': 'Aucun ID de projet fourni'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier que l'utilisateur a accès aux projets
    projects = Project.objects.filter(id__in=project_ids)
    if projects.count() != len(project_ids):
        return Response(
            {'error': 'Certains projets sont introuvables'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Effectuer la suppression
    deleted_count, _ = projects.delete()
    
    return Response({
        'message': f'{deleted_count} projets supprimés avec succès',
        'deleted_count': deleted_count
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_dashboard(request):
    """Tableau de bord des projets pour l'utilisateur connecté"""
    user = request.user
    
    # Projets créés par l'utilisateur
    my_projects = Project.objects.filter(created_by=user)
    
    # Projets assignés à l'utilisateur
    assigned_projects = Project.objects.filter(assigned_to=user)
    
    # Tâches assignées à l'utilisateur
    my_tasks = ProjectTask.objects.filter(assigned_to=user, is_completed=False)
    
    # Projets en retard
    today = timezone.now().date()
    overdue_projects = Project.objects.filter(
        Q(created_by=user) | Q(assigned_to=user),
        deadline__lt=today,
        status__in=[ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS]
    ).distinct()
    
    # Projets récents
    recent_projects = Project.objects.filter(
        Q(created_by=user) | Q(assigned_to=user)
    ).distinct().order_by('-created_at')[:5]
    
    dashboard_data = {
        'my_projects_count': my_projects.count(),
        'assigned_projects_count': assigned_projects.count(),
        'pending_tasks_count': my_tasks.count(),
        'overdue_projects_count': overdue_projects.count(),
        'recent_projects': ProjectListSerializer(recent_projects, many=True).data,
        'overdue_projects': ProjectListSerializer(overdue_projects, many=True).data
    }
    
    return Response(dashboard_data)
