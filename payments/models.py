
from django.db import models
from accounts.models import User
class Payment(models.Model):
    METHOD = [("virtual_card","Carte Virtuelle"),("cod","Cash Livraison"),("baridimob","Baridimob")]
    STATUS = [("pending","En attente"),("completed","Complété"),("failed","Échoué"),("refunded","Remboursé")]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    order      = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="payment", null=True, blank=True)
    method     = models.CharField(max_length=20, choices=METHOD)
    amount     = models.DecimalField(max_digits=12, decimal_places=2)
    status     = models.CharField(max_length=20, choices=STATUS, default="pending")
    reference  = models.CharField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]
    def __str__(self): return f"#{self.reference} — {self.amount} DA"
    def save(self,*a,**k):
        if not self.reference:
            import uuid; self.reference="PAY-"+str(uuid.uuid4())[:12].upper()
        super().save(*a,**k)
