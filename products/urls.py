
from django.urls import path
from . import views
app_name = "products"
urlpatterns = [
    path("",                    views.catalog,               name="catalog"),
    path("categories/",         views.categories_page,       name="categories"),
    path("search/",             views.search_autocomplete,   name="search"),
    path("add/",                views.product_create,        name="create"),
    path("<slug:slug>/",        views.product_detail,        name="detail"),
    path("<slug:slug>/edit/",   views.product_edit,          name="edit"),
    path("<slug:slug>/delete/", views.product_delete,        name="delete"),
]
