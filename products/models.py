
from django.db import models
from django.utils import timezone
from stores.models import Store

class Category(models.Model):
    name      = models.CharField(max_length=100)
    slug      = models.SlugField(unique=True)
    icon      = models.CharField(max_length=10, default="📦")
    is_active = models.BooleanField(default=True)
    order     = models.PositiveSmallIntegerField(default=0)
    class Meta:
        verbose_name_plural="Catégories"; ordering=["order","name"]
    def __str__(self): return self.name
    def save(self,*a,**k):
        if not self.slug:
            from django.utils.text import slugify; self.slug=slugify(self.name)
        super().save(*a,**k)

class Product(models.Model):
    STATUS = [("active","Actif"),("sold_out","Épuisé"),("expired","Expiré"),("draft","Brouillon")]
    store          = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category       = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    name           = models.CharField(max_length=200)
    slug           = models.SlugField(max_length=220, unique=True, blank=True)
    description    = models.TextField(blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price  = models.DecimalField(max_digits=10, decimal_places=2)
    discount_pct   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    expiry_date    = models.DateField()
    quantity       = models.PositiveIntegerField(default=0)
    unit           = models.CharField(max_length=30, default="unité")
    weight_grams   = models.PositiveIntegerField(null=True, blank=True)
    barcode        = models.CharField(max_length=50, blank=True)
    status         = models.CharField(max_length=20, choices=STATUS, default="active")
    is_featured    = models.BooleanField(default=False)
    views_count    = models.PositiveIntegerField(default=0)
    sales_count    = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural="Produits"; ordering=["-created_at"]
    def __str__(self): return self.name
    def save(self,*a,**k):
        if not self.slug:
            from django.utils.text import slugify; import uuid
            self.slug = slugify(self.name)+"-"+str(uuid.uuid4())[:6]
        super().save(*a,**k)
    @property
    def days_until_expiry(self):
        return (self.expiry_date - timezone.now().date()).days
    @property
    def expiry_urgency(self):
        d = self.days_until_expiry
        if d < 0: return "expired"
        if d <= 3: return "urgent"
        if d <= 7: return "warning"
        return "safe"
    @property
    def savings(self): return self.original_price - self.current_price
    @property
    def is_expired(self): return self.days_until_expiry < 0

class ProductImage(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image      = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)
    order      = models.PositiveSmallIntegerField(default=0)
    class Meta: ordering=["order"]
