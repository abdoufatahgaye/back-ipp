from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ProjectCategory, Project, ProjectImage, ProjectTask, 
    ProjectComment, ProjectDocument
)

User = get_user_model()


class ProjectCategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories de projets"""
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectCategory
        fields = ['id', 'name', 'description', 'icon', 'projects_count', 'created_at']

    def get_projects_count(self, obj):
        return obj.projects.count()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer basique pour les utilisateurs"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ProjectImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images de projets"""
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'alt_text', 'caption', 'order', 'uploaded_at']


class ProjectTaskSerializer(serializers.ModelSerializer):
    """Serializer pour les tâches de projets"""
    assigned_to_details = UserBasicSerializer(source='assigned_to', read_only=True)

    class Meta:
        model = ProjectTask
        fields = [
            'id', 'title', 'description', 'is_completed', 'due_date', 
            'completed_at', 'assigned_to', 'assigned_to_details', 'order', 
            'priority', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        if data.get('is_completed') and not data.get('completed_at'):
            from django.utils import timezone
            data['completed_at'] = timezone.now()
        elif not data.get('is_completed'):
            data['completed_at'] = None
        return data


class ProjectCommentSerializer(serializers.ModelSerializer):
    """Serializer pour les commentaires de projets"""
    author_details = UserBasicSerializer(source='author', read_only=True)

    class Meta:
        model = ProjectComment
        fields = [
            'id', 'content', 'is_internal', 'author', 'author_details',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ProjectDocumentSerializer(serializers.ModelSerializer):
    """Serializer pour les documents de projets"""
    uploaded_by_details = UserBasicSerializer(source='uploaded_by', read_only=True)

    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'title', 'description', 'file_path', 'file_type', 
            'file_size', 'uploaded_by', 'uploaded_by_details', 'uploaded_at'
        ]

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des projets (vue simplifiée)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'category_name', 'client_name',
            'city', 'status', 'priority', 'start_date', 'end_date', 'deadline',
            'estimated_budget', 'progress_percentage', 'main_image',
            'created_by_name', 'tasks_count', 'completed_tasks_count',
            'is_overdue', 'duration_days', 'created_at', 'updated_at'
        ]

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    def get_completed_tasks_count(self, obj):
        return obj.tasks.filter(is_completed=True).count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un projet"""
    category = ProjectCategorySerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    assigned_to = UserBasicSerializer(many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)
    tasks = ProjectTaskSerializer(many=True, read_only=True)
    comments = ProjectCommentSerializer(many=True, read_only=True)
    documents = ProjectDocumentSerializer(many=True, read_only=True)
    
    # Champs calculés
    tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    pending_tasks_count = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()
    budget_variance = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'category', 'client_name',
            'client_email', 'client_phone', 'address', 'city', 'postal_code',
            'region', 'status', 'priority', 'start_date', 'end_date', 'deadline',
            'estimated_budget', 'actual_budget', 'progress_percentage',
            'specifications', 'notes', 'tags', 'main_image', 'created_by',
            'assigned_to', 'images', 'tasks', 'comments', 'documents',
            'tasks_count', 'completed_tasks_count', 'pending_tasks_count',
            'is_overdue', 'duration_days', 'budget_variance',
            'created_at', 'updated_at'
        ]

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    def get_completed_tasks_count(self, obj):
        return obj.tasks.filter(is_completed=True).count()

    def get_pending_tasks_count(self, obj):
        return obj.tasks.filter(is_completed=False).count()

    def get_budget_variance(self, obj):
        """Calcule l'écart budgétaire"""
        if obj.estimated_budget and obj.actual_budget:
            return float(obj.actual_budget - obj.estimated_budget)
        return None


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier un projet"""
    assigned_to_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'title', 'description', 'category', 'client_name', 'client_email',
            'client_phone', 'address', 'city', 'postal_code', 'region',
            'status', 'priority', 'start_date', 'end_date', 'deadline',
            'estimated_budget', 'actual_budget', 'progress_percentage',
            'specifications', 'notes', 'tags', 'main_image', 'assigned_to_ids'
        ]

    def validate(self, data):
        # Validation des dates
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        deadline = data.get('deadline')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "La date de début ne peut pas être postérieure à la date de fin."
            )

        if start_date and deadline and start_date > deadline:
            raise serializers.ValidationError(
                "La date de début ne peut pas être postérieure à la date limite."
            )

        # Validation du budget
        estimated_budget = data.get('estimated_budget')
        actual_budget = data.get('actual_budget')

        if estimated_budget is not None and estimated_budget < 0:
            raise serializers.ValidationError(
                "Le budget estimé ne peut pas être négatif."
            )

        if actual_budget is not None and actual_budget < 0:
            raise serializers.ValidationError(
                "Le budget réel ne peut pas être négatif."
            )

        return data

    def create(self, validated_data):
        assigned_to_ids = validated_data.pop('assigned_to_ids', [])
        validated_data['created_by'] = self.context['request'].user
        
        project = Project.objects.create(**validated_data)
        
        if assigned_to_ids:
            users = User.objects.filter(id__in=assigned_to_ids)
            project.assigned_to.set(users)
        
        return project

    def update(self, instance, validated_data):
        assigned_to_ids = validated_data.pop('assigned_to_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if assigned_to_ids is not None:
            users = User.objects.filter(id__in=assigned_to_ids)
            instance.assigned_to.set(users)
        
        return instance


class ProjectStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des projets"""
    total_projects = serializers.IntegerField()
    projects_by_status = serializers.DictField()
    projects_by_priority = serializers.DictField()
    projects_by_category = serializers.DictField()
    overdue_projects = serializers.IntegerField()
    total_budget = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_progress = serializers.FloatField()
    recent_projects = ProjectListSerializer(many=True)


class ProjectBulkUpdateSerializer(serializers.Serializer):
    """Serializer pour les mises à jour en lot"""
    project_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    update_data = serializers.DictField()

    def validate_update_data(self, value):
        allowed_fields = [
            'status', 'priority', 'progress_percentage', 'estimated_budget',
            'actual_budget', 'start_date', 'end_date', 'deadline'
        ]
        
        for field in value.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(
                    f"Le champ '{field}' n'est pas autorisé pour la mise à jour en lot."
                )
        
        return value