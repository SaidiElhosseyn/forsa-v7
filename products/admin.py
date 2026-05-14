
from django.contrib import admin
from .models import Category, Product, ProductImage
class PImgInline(admin.TabularInline):
    model = ProductImage; extra = 1
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["icon","name","is_active","order"]
    list_editable = ["is_active","order"]
    readonly_fields = ["slug"]
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name","store","category","current_price","discount_pct","expiry_date","quantity","status"]
    list_filter  = ["status","category"]
    search_fields= ["name","store__name"]
    readonly_fields = ["slug","views_count","sales_count","created_at"]
    inlines = [PImgInline]
    list_editable = ["status"]
    date_hierarchy = "expiry_date"
