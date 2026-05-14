
from django.contrib import admin
from .models import Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display=["reference","user","method","amount","status","created_at"]
    list_filter=["status","method"]; readonly_fields=["reference","created_at"]
