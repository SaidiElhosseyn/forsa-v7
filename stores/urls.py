from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('',              views.stores_list,  name='list'),
    path('map/',          views.store_map,    name='map'),       # ← Carte interactive
    path('create/',       views.store_create, name='create'),
    path('mine/',         views.my_store,     name='my_store'),
    path('edit/',         views.store_edit,   name='edit'),
    path('<slug:slug>/',  views.store_detail, name='detail'),
]
