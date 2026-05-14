
from django.db import models
from accounts.models import User
from products.models import Product
class Review(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer   = models.ForeignKey(User,    on_delete=models.CASCADE, related_name="reviews")
    rating     = models.PositiveSmallIntegerField(choices=[(i,i) for i in range(1,6)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together=["product","customer"]; ordering=["-created_at"]
    def __str__(self): return f"{self.customer} → {self.product} ({self.rating}★)"
