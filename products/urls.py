from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # ==================== CATEGORIES ====================
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # ==================== SUPPLIERS ====================
    path('suppliers/', views.SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    
    # ==================== PRODUCTS ====================
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/search/', views.product_search, name='product-search'),
    path('products/<uuid:product_id>/recommendations/', views.product_recommendations, name='product-recommendations'),
    
    # ==================== PRODUCT REVIEWS ====================
    path('products/<uuid:product_id>/reviews/', views.ProductReviewListCreateView.as_view(), name='product-review-list-create'),
    path('reviews/<int:pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),
    
    # ==================== PRODUCT IMAGES ====================
    path('products/<uuid:product_id>/images/', views.ProductImageListCreateView.as_view(), name='product-image-list-create'),
    path('images/<int:pk>/', views.ProductImageDetailView.as_view(), name='product-image-detail'),
    
    # ==================== STATISTICS ====================
    path('statistics/', views.product_statistics, name='product-statistics'),
    
    # ==================== BULK OPERATIONS ====================
    path('products/bulk-update/', views.bulk_update_products, name='bulk-update-products'),
    path('products/bulk-delete/', views.bulk_delete_products, name='bulk-delete-products'),
]