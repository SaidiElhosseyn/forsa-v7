
from django.db import models
class DiscountRule(models.Model):
    name           = models.CharField(max_length=100)
    days_threshold = models.PositiveIntegerField()
    discount_pct   = models.DecimalField(max_digits=5, decimal_places=2)
    is_active      = models.BooleanField(default=True)
    order          = models.PositiveSmallIntegerField(default=0)
    class Meta: verbose_name="Règle de réduction"; ordering=["order","days_threshold"]
    def __str__(self): return f"{self.name}: -{self.discount_pct}% si ≤{self.days_threshold}j"
