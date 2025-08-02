from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Q, Avg, Count
from .models import Category, Supplier, Product, ProductReview, ProductImage
from .serializers import (
    CategorySerializer, SupplierSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer, 
    ProductReviewSerializer, ProductImageSerializer
)


# ==================== CATEGORIES ====================

class CategoryListCreateView(generics.ListCreateAPIView):
    """Liste et création des catégories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'une catégorie"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


# ==================== SUPPLIERS ====================

class SupplierListCreateView(generics.ListCreateAPIView):
    """Liste et création des fournisseurs"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name', 'location']
    ordering_fields = ['company_name', 'rating', 'created_at']
    ordering = ['-rating']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'un fournisseur"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]


# ==================== PRODUCTS ====================

class ProductListCreateView(generics.ListCreateAPIView):
    """Liste et création des produits"""
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'supplier', 'in_stock', 'unit']
    search_fields = ['name', 'description', 'supplier__company_name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres personnalisés
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        category_name = self.request.query_params.get('category_name')
        supplier_name = self.request.query_params.get('supplier_name')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)
        if supplier_name:
            queryset = queryset.filter(supplier__company_name__icontains=supplier_name)
            
        return queryset.select_related('category', 'supplier')


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'un produit"""
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_search(request):
    """Recherche avancée de produits"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'results': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(supplier__company_name__icontains=query),
        is_active=True
    ).select_related('category', 'supplier')[:20]
    
    serializer = ProductListSerializer(products, many=True)
    return Response({'results': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_recommendations(request, product_id):
    """Produits recommandés basés sur la catégorie"""
    try:
        product = Product.objects.get(id=product_id)
        recommendations = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product_id)[:6]
        
        serializer = ProductListSerializer(recommendations, many=True)
        return Response({'recommendations': serializer.data})
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé'}, status=status.HTTP_404_NOT_FOUND)


# ==================== PRODUCT REVIEWS ====================

class ProductReviewListCreateView(generics.ListCreateAPIView):
    """Liste et création des avis produits"""
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        serializer.save(
            user=self.request.user,
            product_id=product_id
        )


class ProductReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'un avis"""
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductReview.objects.filter(user=self.request.user)


# ==================== PRODUCT IMAGES ====================

class ProductImageListCreateView(generics.ListCreateAPIView):
    """Liste et ajout d'images pour un produit"""
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductImage.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        serializer.save(product_id=product_id)


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'une image"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]


# ==================== STATISTICS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_statistics(request):
    """Statistiques des produits"""
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    products_in_stock = Product.objects.filter(is_active=True, in_stock=True).count()
    
    # Top catégories
    top_categories = Category.objects.annotate(
        product_count=models.Count('products', filter=models.Q(products__is_active=True))
    ).order_by('-product_count')[:5]
    
    # Top fournisseurs
    top_suppliers = Supplier.objects.annotate(
        product_count=models.Count('products', filter=models.Q(products__is_active=True))
    ).order_by('-product_count')[:5]
    
    return Response({
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'products_in_stock': products_in_stock,
        'top_categories': [
            {'name': cat.name, 'product_count': cat.product_count}
            for cat in top_categories
        ],
        'top_suppliers': [
            {'name': sup.company_name, 'product_count': sup.product_count}
            for sup in top_suppliers
        ]
    })


# ==================== BULK OPERATIONS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_update_products(request):
    """Mise à jour en lot des produits"""
    product_ids = request.data.get('product_ids', [])
    update_data = request.data.get('update_data', {})
    
    if not product_ids or not update_data:
        return Response(
            {'error': 'product_ids et update_data sont requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Filtrer les champs autorisés pour la mise à jour en lot
    allowed_fields = ['in_stock', 'is_active', 'delivery_time']
    filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    if not filtered_data:
        return Response(
            {'error': 'Aucun champ valide pour la mise à jour'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    updated_count = Product.objects.filter(
        id__in=product_ids
    ).update(**filtered_data)
    
    return Response({
        'message': f'{updated_count} produits mis à jour',
        'updated_count': updated_count
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bulk_delete_products(request):
    """Suppression en lot des produits"""
    product_ids = request.data.get('product_ids', [])
    
    if not product_ids:
        return Response(
            {'error': 'product_ids est requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    deleted_count, _ = Product.objects.filter(
        id__in=product_ids
    ).delete()
    
    return Response({
        'message': f'{deleted_count} produits supprimés',
        'deleted_count': deleted_count
    })
