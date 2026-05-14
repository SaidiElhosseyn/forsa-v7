
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VirtualCard

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username","email","get_full_name","role","wilaya","is_verified","date_joined"]
    list_filter  = ["role","is_verified","wilaya"]
    search_fields= ["username","email","first_name","last_name"]
    fieldsets = UserAdmin.fieldsets + (
        ("Infos supplémentaires",{"fields":("role","phone","wilaya","address","avatar","is_verified")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Infos supplémentaires",{"fields":("role","phone","wilaya","first_name","last_name","email")}),
    )

@admin.register(VirtualCard)
class VirtualCardAdmin(admin.ModelAdmin):
    list_display = ["user","card_number","balance","is_active","created_at"]
    list_filter  = ["is_active"]
    readonly_fields = ["card_number","created_at"]
