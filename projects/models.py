from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class ProjectCategory(models.Model):
    """Catégories de projets BTP"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie de projet"
        verbose_name_plural = "Catégories de projets"
        ordering = ['name']

    def __str__(self):
        return self.name


class ProjectStatus(models.TextChoices):
    """Statuts possibles d'un projet"""
    PLANNING = 'planning', 'En planification'
    IN_PROGRESS = 'in_progress', 'En cours'
    ON_HOLD = 'on_hold', 'En pause'
    COMPLETED = 'completed', 'Terminé'
    CANCELLED = 'cancelled', 'Annulé'


class ProjectPriority(models.TextChoices):
    """Priorités d'un projet"""
    LOW = 'low', 'Faible'
    MEDIUM = 'medium', 'Moyenne'
    HIGH = 'high', 'Élevée'
    URGENT = 'urgent', 'Urgente'


class Project(models.Model):
    """Modèle principal pour les projets BTP"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    category = models.ForeignKey(
        ProjectCategory, 
        on_delete=models.CASCADE, 
        related_name='projects',
        verbose_name="Catégorie"
    )
    
    # Informations du client/propriétaire
    client_name = models.CharField(max_length=100, verbose_name="Nom du client")
    client_email = models.EmailField(verbose_name="Email du client")
    client_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone du client")
    
    # Localisation
    address = models.TextField(verbose_name="Adresse")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    region = models.CharField(max_length=100, verbose_name="Région")
    
    # Gestion du projet
    status = models.CharField(
        max_length=20, 
        choices=ProjectStatus.choices, 
        default=ProjectStatus.PLANNING,
        verbose_name="Statut"
    )
    priority = models.CharField(
        max_length=10, 
        choices=ProjectPriority.choices, 
        default=ProjectPriority.MEDIUM,
        verbose_name="Priorité"
    )
    
    # Dates
    start_date = models.DateField(null=True, blank=True, verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    deadline = models.DateField(null=True, blank=True, verbose_name="Date limite")
    
    # Budget
    estimated_budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Budget estimé"
    )
    actual_budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Budget réel"
    )
    
    # Progression
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Pourcentage d'avancement"
    )
    
    # Métadonnées
    specifications = models.JSONField(default=dict, blank=True, verbose_name="Spécifications techniques")
    notes = models.TextField(blank=True, verbose_name="Notes")
    tags = models.JSONField(default=list, blank=True, verbose_name="Tags")
    
    # Images
    main_image = models.CharField(max_length=255, blank=True, verbose_name="Image principale")
    
    # Gestion
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_projects',
        verbose_name="Créé par"
    )
    assigned_to = models.ManyToManyField(
        User, 
        blank=True, 
        related_name='assigned_projects',
        verbose_name="Assigné à"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
            models.Index(fields=['city']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.client_name}"

    @property
    def is_overdue(self):
        """Vérifie si le projet est en retard"""
        if self.deadline and self.status not in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]:
            from django.utils import timezone
            return timezone.now().date() > self.deadline
        return False

    @property
    def duration_days(self):
        """Calcule la durée du projet en jours"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None


class ProjectImage(models.Model):
    """Images associées aux projets"""
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Projet"
    )
    image = models.CharField(max_length=255, verbose_name="Chemin de l'image")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Texte alternatif")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Légende")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image de projet"
        verbose_name_plural = "Images de projets"
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"Image {self.order} - {self.project.title}"


class ProjectTask(models.Model):
    """Tâches d'un projet"""
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        verbose_name="Projet"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Statut de la tâche
    is_completed = models.BooleanField(default=False, verbose_name="Terminée")
    
    # Dates
    due_date = models.DateField(null=True, blank=True, verbose_name="Date d'échéance")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminée le")
    
    # Assignation
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='project_tasks',
        verbose_name="Assignée à"
    )
    
    # Ordre et priorité
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    priority = models.CharField(
        max_length=10, 
        choices=ProjectPriority.choices, 
        default=ProjectPriority.MEDIUM,
        verbose_name="Priorité"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tâche de projet"
        verbose_name_plural = "Tâches de projets"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.project.title} - {self.title}"


class ProjectComment(models.Model):
    """Commentaires sur les projets"""
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name="Projet"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Auteur"
    )
    content = models.TextField(verbose_name="Contenu")
    is_internal = models.BooleanField(
        default=False, 
        verbose_name="Commentaire interne",
        help_text="Les commentaires internes ne sont visibles que par l'équipe"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commentaire de projet"
        verbose_name_plural = "Commentaires de projets"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.project.title}"


class ProjectDocument(models.Model):
    """Documents associés aux projets"""
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name="Projet"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    file_path = models.CharField(max_length=500, verbose_name="Chemin du fichier")
    file_type = models.CharField(max_length=50, verbose_name="Type de fichier")
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Taille du fichier")
    
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Téléchargé par"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Document de projet"
        verbose_name_plural = "Documents de projets"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.project.title}"
