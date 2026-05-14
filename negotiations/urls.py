from django.urls import path
from . import views

app_name = 'negotiations'

urlpatterns = [
    # Liste de toutes les négociations de l'utilisateur connecté
    path('',
         views.my_negotiations,
         name='list'),

    # Démarrer une négociation sur un produit
    path('start/<slug:slug>/',
         views.start,
         name='start'),

    # Détail / timeline d'une négociation
    path('<int:pk>/',
         views.detail,
         name='detail'),

    # Réponse du vendeur (AJAX POST)
    path('<int:pk>/vendor-respond/',
         views.vendor_respond,
         name='vendor_respond'),

    # Réponse de l'acheteur à une contre-offre (AJAX POST)
    path('<int:pk>/buyer-respond/',
         views.buyer_respond,
         name='buyer_respond'),

    # Annuler une négociation
    path('<int:pk>/cancel/',
         views.cancel,
         name='cancel'),

    # Créer une commande depuis une négociation acceptée
    path('<int:pk>/order/',
         views.create_order_from_deal,
         name='create_order'),
]
