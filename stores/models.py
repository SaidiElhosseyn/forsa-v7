from django.db import models
from accounts.models import User


class Store(models.Model):
    STATUS = [
        ("pending",   "En attente"),
        ("active",    "Active"),
        ("suspended", "Suspendue"),
    ]
    owner       = models.OneToOneField(User, on_delete=models.CASCADE,
                                       related_name="store",
                                       limit_choices_to={"role": "vendor"})
    name        = models.CharField(max_length=150)
    slug        = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo        = models.ImageField(upload_to="stores/logos/",   blank=True, null=True)
    banner      = models.ImageField(upload_to="stores/banners/", blank=True, null=True)
    phone       = models.CharField(max_length=20, blank=True)
    wilaya      = models.CharField(max_length=2,  blank=True)
    address     = models.TextField(blank=True)
    # ── GPS coordinates (for map feature) ──
    latitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # ────────────────────────────────────────
    status      = models.CharField(max_length=20, choices=STATUS, default="active")
    rating      = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_sales = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Boutique"
        verbose_name_plural = "Boutiques"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = slugify(self.name) + "-" + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def has_location(self):
        return self.latitude is not None and self.longitude is not None
