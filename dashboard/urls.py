from django.urls import path
from . import views
app_name = 'dashboard'
urlpatterns = [
    path('',         views.dashboard_index,    name='index'),
    path('admin/',   views.admin_dashboard,    name='admin'),
    path('vendor/',  views.vendor_dashboard,   name='vendor'),
    path('customer/', views.customer_dashboard, name='customer'),
    path('vendor/revenue/', views.vendor_revenue,   name='vendor_revenue'),
    path('vendor/stats/',   views.vendor_stats,     name='vendor_stats')
]
