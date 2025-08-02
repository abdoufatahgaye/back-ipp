from rest_framework import serializers
from .models import Category, Supplier, Product, ProductReview, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories"""
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer pour les fournisseurs"""
    products_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id', 'company_name', 'location', 'phone', 'email', 
            'description', 'rating', 'certifications', 'products_count',
            'average_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()

    def get_average_rating(self, obj):
        reviews = ProductReview.objects.filter(product__supplier=obj)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0.0


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images de produits"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'order', 'created_at']
        read_only_fields = ['created_at']


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer pour les avis produits"""
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            'id', 'rating', 'comment', 'user_name', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des produits (vue simplifiée)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_rating = serializers.DecimalField(source='supplier.rating', max_digits=3, decimal_places=1, read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category_name', 'supplier_name', 'supplier_rating',
            'price', 'unit', 'image', 'in_stock', 'delivery_time', 
            'average_rating', 'reviews_count', 'created_at'
        ]

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0.0

    def get_reviews_count(self, obj):
        return obj.reviews.count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un produit"""
    category = CategorySerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    # Pour la création/modification
    category_id = serializers.IntegerField(write_only=True)
    supplier_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_id', 'supplier', 'supplier_id',
            'price', 'unit', 'description', 'specifications', 'image', 'images',
            'in_stock', 'delivery_time', 'min_order', 'is_active',
            'reviews', 'additional_images', 'average_rating', 'reviews_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0.0

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def validate_category_id(self, value):
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Catégorie invalide.")
        return value

    def validate_supplier_id(self, value):
        try:
            Supplier.objects.get(id=value)
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Fournisseur invalide.")
        return value


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier un produit"""
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'supplier', 'price', 'unit', 'description',
            'specifications', 'image', 'images', 'in_stock', 'delivery_time',
            'min_order', 'is_active'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à 0.")
        return value

    def validate_min_order(self, value):
        if value <= 0:
            raise serializers.ValidationError("La commande minimum doit être supérieure à 0.")
        return value