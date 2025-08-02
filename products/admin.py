from django.contrib import admin
from .models import Category, Supplier, Product, ProductReview, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    ordering = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'location', 'rating', 'phone', 'email', 'created_at']
    search_fields = ['company_name', 'location', 'email']
    list_filter = ['location', 'rating', 'created_at']
    ordering = ['-rating', 'company_name']
    readonly_fields = ['created_at', 'updated_at']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order']


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']
    can_delete = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'supplier', 'price', 'unit', 
        'in_stock', 'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'supplier', 'unit', 'in_stock', 
        'is_active', 'created_at'
    ]
    search_fields = ['name', 'description', 'supplier__company_name']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductReviewInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'name', 'category', 'supplier', 'description')
        }),
        ('Prix et unités', {
            'fields': ('price', 'unit', 'min_order')
        }),
        ('Images', {
            'fields': ('image', 'images')
        }),
        ('Spécifications', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Disponibilité', {
            'fields': ('in_stock', 'delivery_time', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'supplier')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'product__category']
    search_fields = ['product__name', 'user__username', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'order', 'created_at']
    list_filter = ['created_at', 'product__category']
    search_fields = ['product__name', 'alt_text']
    ordering = ['product', 'order']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
