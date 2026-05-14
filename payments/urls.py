from django.urls import path
from . import views
app_name = 'payments'
urlpatterns = [
    path('virtual-card/', views.virtual_card_view, name='virtual_card'),
    path('history/',      views.payment_history,  name='history'),
]
