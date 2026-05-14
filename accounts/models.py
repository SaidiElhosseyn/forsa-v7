from django.contrib.auth.models import AbstractUser
from django.db import models

WILAYA_CHOICES = [
    ('01','Adrar'),('02','Chlef'),('03','Laghouat'),('04','Oum El Bouaghi'),('05','Batna'),
    ('06','Béjaïa'),('07','Biskra'),('08','Béchar'),('09','Blida'),('10','Bouira'),
    ('11','Tamanrasset'),('12','Tébessa'),('13','Tlemcen'),('14','Tiaret'),('15','Tizi Ouzou'),
    ('16','Alger'),('17','Djelfa'),('18','Jijel'),('19','Sétif'),('20','Saïda'),
    ('21','Skikda'),('22','Sidi Bel Abbès'),('23','Annaba'),('24','Guelma'),('25','Constantine'),
    ('26','Médéa'),('27','Mostaganem'),('28',"M'Sila"),('29','Mascara'),('30','Ouargla'),
    ('31','Oran'),('32','El Bayadh'),('33','Illizi'),('34','Bordj Bou Arréridj'),('35','Boumerdès'),
    ('36','El Tarf'),('37','Tindouf'),('38','Tissemsilt'),('39','El Oued'),('40','Khenchela'),
    ('41','Souk Ahras'),('42','Tipaza'),('43','Mila'),('44','Aïn Defla'),('45','Naâma'),
    ('46','Aïn Témouchent'),('47','Ghardaïa'),('48','Relizane'),
]
_WILAYA_DICT = dict(WILAYA_CHOICES)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin','Administrateur'),('vendor','Vendeur'),('customer','Acheteur'),
    ]
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone       = models.CharField(max_length=20, blank=True)
    wilaya      = models.CharField(max_length=2, choices=WILAYA_CHOICES, blank=True)
    address     = models.TextField(blank=True)
    avatar      = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name='Utilisateur'
        verbose_name_plural='Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ── Role helpers ──────────────────────────────────────
    @property
    def is_vendor(self):      return self.role == 'vendor'
    @property
    def is_customer(self):    return self.role == 'customer'
    @property
    def is_admin_user(self):  return self.role == 'admin' or self.is_superuser

    # ── Wilaya helpers ────────────────────────────────────
    def get_wilaya_name(self):
        return _WILAYA_DICT.get(self.wilaya, '')

    # Alias used in templates (get_wilaya_display_name)
    def get_wilaya_display_name(self):
        return _WILAYA_DICT.get(self.wilaya, self.wilaya)


class Wishlist(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField('products.Product', blank=True, related_name='wishlisted_by')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Liste de favoris'

    def __str__(self):
        return f"Favoris de {self.user.username}"


class VirtualCard(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='virtual_card')
    card_number = models.CharField(max_length=16, unique=True, blank=True)
    balance     = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name='Carte Virtuelle'

    def __str__(self):
        return f"Carte {self.user.username} — {self.balance} DA"

    def save(self, *args, **kwargs):
        if not self.card_number:
            import random
            self.card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        super().save(*args, **kwargs)
