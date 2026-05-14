"""
Injecte dans TOUS les templates :
  - nav_categories : catégories actives (depuis DB uniquement)
  - cart_items_count : nb articles panier de l'utilisateur connecté
"""
from .models import Category


def categories_context(request):
    ctx = {
        'nav_categories': Category.objects.filter(is_active=True).order_by('order'),
        'cart_items_count': 0,
    }
    # Cart count — uniquement pour les clients connectés
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'customer':
        try:
            from orders.models import Cart
            cart = Cart.objects.get(customer=request.user)
            ctx['cart_items_count'] = cart.cart_items.count()
        except Exception:
            ctx['cart_items_count'] = 0
    return ctx
