from django.contrib import admin
from .models import Negotiation

@admin.register(Negotiation)
class NegotiationAdmin(admin.ModelAdmin):
    list_display   = ['pk','product','buyer','vendor','buyer_price',
                      'counter_price','final_price','status','created_at']
    list_filter    = ['status','created_at']
    search_fields  = ['product__name','buyer__username','vendor__username']
    readonly_fields= ['created_at','updated_at','expires_at']
    ordering       = ['-created_at']
