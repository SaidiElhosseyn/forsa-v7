from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from products.models import Product


class Negotiation(models.Model):
    """
    Machine d'états :
    ┌──────────────┐
    │    DRAFT     │  ← acheteur remplit le formulaire (pas encore soumis)
    └──────┬───────┘
           │ submit
    ┌──────▼───────┐
    │  EN_ATTENTE  │  ← vendeur doit répondre dans 24h
    └──────┬───────┘
           ├─ accepte  ──────────────►  ACCEPTÉE  ──► commande créée
           ├─ refuse   ──────────────►  REFUSÉE
           └─ contre-offre ──────────►  CONTRE_OFFRE
                                              │
                                    ┌─────────┴──────────┐
                                    │ acheteur accepte   │ acheteur refuse
                                    ▼                    ▼
                                ACCEPTÉE              REFUSÉE
                                    │
                                commande créée
    """
    STATUS = [
        ('pending',       'En attente vendeur'),
        ('counter',       'Contre-offre en cours'),
        ('accepted',      'Acceptée ✅'),
        ('rejected',      'Refusée ❌'),
        ('ordered',       'Commandée 🛒'),
        ('expired',       'Expirée ⏰'),
        ('cancelled',     'Annulée'),
    ]

    # ── Parties ───────────────────────────────────────────────
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='negotiations'
    )
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='negotiations_as_buyer'
    )
    # Vendor = product.store.owner — dénormalisé pour les queries
    vendor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='negotiations_as_vendor'
    )

    # ── Prix ──────────────────────────────────────────────────
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Prix du produit au moment de la négociation"
    )
    buyer_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Prix proposé par l'acheteur"
    )
    counter_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Contre-offre du vendeur (si applicable)"
    )
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Prix finalement accepté"
    )

    # ── Messages ──────────────────────────────────────────────
    buyer_message  = models.TextField(blank=True, help_text="Message optionnel de l'acheteur")
    vendor_message = models.TextField(blank=True, help_text="Réponse optionnelle du vendeur")
    counter_message = models.TextField(blank=True, help_text="Message avec la contre-offre")
    buyer_counter_message = models.TextField(blank=True, help_text="Réponse de l'acheteur à la contre-offre")

    # ── Statut ────────────────────────────────────────────────
    status     = models.CharField(max_length=20, choices=STATUS, default='pending')
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Lien vers la commande créée (si négociation aboutie)
    order = models.OneToOneField(
        'orders.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='negotiation'
    )

    class Meta:
        ordering           = ['-created_at']
        verbose_name       = 'Négociation'
        verbose_name_plural = 'Négociations'

    def __str__(self):
        return f"Négo #{self.pk} — {self.product.name} | {self.buyer} → {self.vendor}"

    # ── Properties ────────────────────────────────────────────
    @property
    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    @property
    def is_active(self):
        return self.status in ('pending', 'counter') and not self.is_expired

    @property
    def discount_from_original(self):
        """% de réduction par rapport au prix original."""
        if self.final_price and self.original_price:
            return round((1 - float(self.final_price) / float(self.original_price)) * 100, 1)
        return 0

    @property
    def buyer_discount_pct(self):
        return round((1 - float(self.buyer_price) / float(self.original_price)) * 100, 1)

    @property
    def time_remaining(self):
        """Secondes restantes avant expiration."""
        if not self.expires_at:
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, int(delta.total_seconds()))

    # ── Lifecycle helpers ─────────────────────────────────────
    def save(self, *args, **kwargs):
        # Set expiration at creation
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def accept(self, accepted_price=None):
        """Valider la négociation au prix convenu."""
        self.final_price = accepted_price or self.buyer_price
        self.status      = 'accepted'
        self.save(update_fields=['final_price', 'status', 'updated_at'])

    def reject(self):
        self.status = 'rejected'
        self.save(update_fields=['status', 'updated_at'])

    def expire(self):
        self.status = 'expired'
        self.save(update_fields=['status', 'updated_at'])

    def mark_ordered(self, order):
        self.order  = order
        self.status = 'ordered'
        self.save(update_fields=['order', 'status', 'updated_at'])
