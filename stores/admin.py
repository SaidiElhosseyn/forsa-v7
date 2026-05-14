
from django.contrib import admin
from .models import Store
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name","owner","wilaya","status","rating","total_sales"]
    list_editable = ["status"]
    list_filter   = ["status","wilaya"]
    search_fields = ["name","owner__username"]
