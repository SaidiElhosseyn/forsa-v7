
from django.contrib import admin
from .models import DiscountRule
@admin.register(DiscountRule)
class DiscountRuleAdmin(admin.ModelAdmin):
    list_display  = ["name","days_threshold","discount_pct","is_active","order"]
    list_editable = ["discount_pct","is_active","order"]
