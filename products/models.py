from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Category(models.Model):
    """Catégorie de produits"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Fournisseur de produits"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')
    company_name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    location = models.CharField(max_length=100, verbose_name="Localisation")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    description = models.TextField(verbose_name="Description")
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name="Note"
    )
    certifications = models.JSONField(default=list, verbose_name="Certifications")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['company_name']

    def __str__(self):
        return self.company_name


class Product(models.Model):
    """Produit du marketplace"""
    UNIT_CHOICES = [
        ('kg', 'Kilogramme'),
        ('tonne', 'Tonne'),
        ('m', 'Mètre'),
        ('m²', 'Mètre carré'),
        ('m³', 'Mètre cube'),
        ('pièce', 'Pièce'),
        ('lot', 'Lot'),
        ('palette', 'Palette'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nom")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, verbose_name="Unité")
    description = models.TextField(verbose_name="Description")
    specifications = models.JSONField(default=dict, verbose_name="Spécifications")
    image = models.CharField(max_length=500, blank=True, verbose_name="Image principale")
    images = models.JSONField(default=list, verbose_name="Galerie d'images")
    in_stock = models.BooleanField(default=True, verbose_name="En stock")
    delivery_time = models.CharField(max_length=50, verbose_name="Délai de livraison")
    min_order = models.PositiveIntegerField(default=1, verbose_name="Commande minimum")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.supplier.company_name}"


class ProductReview(models.Model):
    """Avis sur les produits"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note"
    )
    comment = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis de {self.user.username} sur {self.product.name}"


class ProductImage(models.Model):
    """Images supplémentaires des produits"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/', verbose_name="Image")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Texte alternatif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produits"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image de {self.product.name}"
