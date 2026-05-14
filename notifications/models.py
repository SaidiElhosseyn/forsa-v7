from django.db import models
from accounts.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('order_placed',         'Nouvelle commande'),
        ('order_confirmed',      'Commande confirmée'),
        ('order_cancelled',      'Commande annulée'),
        ('order_shipped',        'Commande expédiée'),
        ('order_delivered',      'Commande livrée'),
        ('expiry_alert',         'Alerte péremption'),
        ('stock_warning',        'Stock faible'),
        ('negotiation_offer',    'Nouvelle offre'),
        ('negotiation_accepted', 'Offre acceptée'),
        ('negotiation_rejected', 'Offre refusée'),
        ('negotiation_counter',  'Contre-offre'),
        ('new_registration',     'Nouvelle inscription'),
        ('new_offer',            'Nouvelle offre disponible'),
        ('system',               'Système'),
    ]
    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type  = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system')
    title       = models.CharField(max_length=200)
    body        = models.TextField(blank=True)
    link        = models.CharField(max_length=300, blank=True)  # URL to redirect on click
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'

    def __str__(self):
        return f"[{self.notif_type}] → {self.recipient.username}"


def send_notification(recipient, notif_type, title, body='', link=''):
    """Helper: créer une notification pour un utilisateur."""
    Notification.objects.create(
        recipient=recipient,
        notif_type=notif_type,
        title=title,
        body=body,
        link=link,
    )
