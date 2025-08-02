from django.urls import path
from . import views

urlpatterns = [
    # ==================== CATÉGORIES DE PROJETS ====================
    path('categories/', views.ProjectCategoryListCreateView.as_view(), name='project-category-list-create'),
    path('categories/<int:pk>/', views.ProjectCategoryDetailView.as_view(), name='project-category-detail'),
    
    # ==================== PROJETS ====================
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<uuid:id>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/search/', views.project_search, name='project-search'),
    path('projects/<uuid:project_id>/recommendations/', views.project_recommendations, name='project-recommendations'),
    
    # ==================== TÂCHES DE PROJETS ====================
    path('projects/<uuid:project_id>/tasks/', views.ProjectTaskListCreateView.as_view(), name='project-task-list-create'),
    path('tasks/<int:pk>/', views.ProjectTaskDetailView.as_view(), name='project-task-detail'),
    
    # ==================== COMMENTAIRES DE PROJETS ====================
    path('projects/<uuid:project_id>/comments/', views.ProjectCommentListCreateView.as_view(), name='project-comment-list-create'),
    path('comments/<int:pk>/', views.ProjectCommentDetailView.as_view(), name='project-comment-detail'),
    
    # ==================== IMAGES DE PROJETS ====================
    path('projects/<uuid:project_id>/images/', views.ProjectImageListCreateView.as_view(), name='project-image-list-create'),
    path('images/<int:pk>/', views.ProjectImageDetailView.as_view(), name='project-image-detail'),
    
    # ==================== DOCUMENTS DE PROJETS ====================
    path('projects/<uuid:project_id>/documents/', views.ProjectDocumentListCreateView.as_view(), name='project-document-list-create'),
    path('documents/<int:pk>/', views.ProjectDocumentDetailView.as_view(), name='project-document-detail'),
    
    # ==================== STATISTIQUES ET TABLEAU DE BORD ====================
    path('projects/statistics/', views.project_statistics, name='project-statistics'),
    path('projects/dashboard/', views.project_dashboard, name='project-dashboard'),
    
    # ==================== OPÉRATIONS EN LOT ====================
    path('projects/bulk-update/', views.project_bulk_update, name='project-bulk-update'),
    path('projects/bulk-delete/', views.project_bulk_delete, name='project-bulk-delete'),
]