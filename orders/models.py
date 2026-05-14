
from django.db import models
from accounts.models import User
from products.models import Product

class Order(models.Model):
    STATUS = [("pending","En attente"),("confirmed","Confirmée"),("processing","En préparation"),
              ("shipped","Expédiée"),("delivered","Livrée"),("cancelled","Annulée"),("refunded","Remboursée")]
    customer         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_number     = models.CharField(max_length=30, unique=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS, default="pending")
    total_amount     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_wilaya  = models.CharField(max_length=2, blank=True)
    delivery_address = models.TextField(blank=True)
    delivery_phone   = models.CharField(max_length=20, blank=True)
    delivery_method  = models.CharField(max_length=20, default="standard")
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    class Meta: ordering=["-created_at"]
    def __str__(self): return f"#{self.order_number}"
    def save(self,*a,**k):
        if not self.order_number:
            import uuid; self.order_number="ORD-"+str(uuid.uuid4())[:10].upper()
        super().save(*a,**k)
    def calculate_total(self):
        self.total_amount = sum(i.subtotal for i in self.items.all())
        self.save(update_fields=["total_amount"])

class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product    = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity   = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    @property
    def subtotal(self): return self.unit_price * self.quantity

class Cart(models.Model):
    customer   = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def total(self): return sum(i.subtotal for i in self.cart_items.all())
    @property
    def items_count(self): return self.cart_items.count()

class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta: unique_together=["cart","product"]
    @property
    def subtotal(self): return self.product.current_price * self.quantity
