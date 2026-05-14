from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/',                              views.cart_view,          name='cart'),
    path('cart/add/<slug:slug>/',              views.cart_add,           name='cart_add'),
    path('cart/update/<int:item_id>/',         views.cart_update,        name='cart_update'),
    path('cart/remove/<int:item_id>/',         views.cart_remove,        name='cart_remove'),
    path('checkout/',                          views.checkout,           name='checkout'),
    path('check-expiry/',                      views.check_expiry_api,   name='check_expiry'),
    path('confirmation/<str:order_number>/',   views.order_confirmation, name='confirmation'),
    path('vendor/<str:order_number>/update/',  views.vendor_update_order, name='vendor_update'),
    path('',                                   views.order_list,         name='list'),
    path('<str:order_number>/',                views.order_detail,       name='detail'),
    path('<str:order_number>/cancel/',         views.order_cancel,       name='cancel'),
]
