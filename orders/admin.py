
from django.contrib import admin
from .models import Order, OrderItem
class OItemInline(admin.TabularInline):
    model = OrderItem; extra = 0; readonly_fields = ["subtotal"]
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number","customer","status","total_amount","delivery_wilaya","created_at"]
    list_editable = ["status"]; list_filter = ["status"]; inlines = [OItemInline]
    readonly_fields = ["order_number","created_at"]
