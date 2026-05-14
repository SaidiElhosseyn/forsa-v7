from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from decimal import Decimal
from accounts.models import WILAYA_CHOICES
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(customer=user)
    return cart


def _parse_delivery_days(days_str):
    """
    Convertit une durée de livraison en nombre de jours (valeur max).

    Formats gérés :
      '24h'   → 1 jour   (24 / 24, arrondi au supérieur)
      '48h'   → 2 jours
      '72h'   → 3 jours
      '1-2j'  → 2 jours  (on prend le max pour être conservateur)
      '2-3j'  → 3 jours
      '3-5j'  → 5 jours
      '5-7j'  → 7 jours
      '4-5j'  → 5 jours
      'Immédiat' → 0 jour (Click & Collect)
    """
    import re, math
    if not days_str:
        return 7
    s = str(days_str).lower().strip()

    # Cas Click & Collect / retrait immédiat
    if 'immed' in s or 'immédiat' in s or s == '0':
        return 0

    # Cas heures : '24h', '48h', '72h'
    # Traiter AVANT le cas jours pour éviter de confondre
    if 'h' in s and 'j' not in s:
        hours = re.findall(r'\d+', s)
        if hours:
            return math.ceil(max(int(h) for h in hours) / 24)
        return 1

    # Cas jours : '1-2j', '2-3j', '3-5j', '5-7j', '4-5j'
    nums = re.findall(r'\d+', s)
    if nums:
        return max(int(x) for x in nums)

    return 7

def _check_expiry_conflicts(items, wilaya, delivery_method):
    """
    Retourne la liste des produits qui expireront AVANT livraison estimée.
    Règle : expiry_date < aujourd'hui + délai_max_livraison
    """
    from delivery.models import get_delivery_cost
    delivery_info = get_delivery_cost(wilaya or '16', delivery_method or 'standard')
    max_days = _parse_delivery_days(delivery_info.get('days', '7'))
    today = timezone.now().date()
    deadline = today + timedelta(days=max_days)
    conflicts = []
    for item in items:
        p = item.product
        if p.expiry_date <= deadline:
            remaining = (p.expiry_date - today).days
            conflicts.append({
                'product':   p,
                'name':      p.name,
                'expiry':    p.expiry_date.strftime('%d/%m/%Y'),
                'remaining': remaining,
                'delivery_days': max_days,
            })
    return conflicts


def _notify_buyer_confirmed(order):
    """Notify the buyer that their order is confirmed."""
    from notifications.models import send_notification
    send_notification(
        recipient=order.customer,
        notif_type='order_confirmed',
        title=f'Commande #{order.order_number} confirmée',
        body=f'Votre commande de {order.total_amount:.0f} DA a été confirmée. Merci !',
        link=f'/orders/{order.order_number}/',
    )


def _notify_vendors(order):
    """Envoie une notification à tous les vendeurs concernés par la commande."""
    from notifications.models import send_notification
    vendors_notified = set()
    for item in order.items.select_related('product__store__owner').all():
        vendor = item.product.store.owner
        if vendor.pk not in vendors_notified:
            send_notification(
                recipient=vendor,
                notif_type='order_placed',
                title=f'🛒 Nouvelle commande #{order.order_number}',
                body=(
                    f'{order.customer.get_full_name() or order.customer.username} '
                    f'vient de commander {order.items.count()} article(s) '
                    f'— Total : {order.total_amount:.0f} DA'
                ),
                link=f'/dashboard/',
            )
            vendors_notified.add(vendor.pk)


# ──────────────────────────────────────────────────────────────
# CART
# ──────────────────────────────────────────────────────────────
@login_required
def cart_view(request):
    if not request.user.is_customer:
        return redirect('dashboard:index')
    cart  = _get_or_create_cart(request.user)
    items = cart.cart_items.select_related(
        'product__store', 'product__category'
    ).prefetch_related('product__images')
    return render(request, 'orders/cart.html', {'cart': cart, 'items': items})


@login_required
@require_POST
def cart_add(request, slug):
    if not request.user.is_customer:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    product = get_object_or_404(Product, slug=slug, status='active')
    try:
        qty = max(1, int(request.POST.get('quantity', 1)))
    except (ValueError, TypeError):
        qty = 1
    if qty > product.quantity:
        return JsonResponse({'success': False,
                             'error': f'Stock disponible : {product.quantity}'})
    cart = _get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity = min(item.quantity + qty, product.quantity)
    else:
        item.quantity = qty
    item.save()
    return JsonResponse({
        'success':    True,
        'message':    f'« {product.name} » ajouté au panier !',
        'cart_count': cart.items_count,
        'cart_total': float(cart.total),
    })


@login_required
@require_POST
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    try:
        qty = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        qty = 1

    # FIX: La quantité minimum via le bouton − est 1.
    # Pour supprimer un article, l'utilisateur doit utiliser le bouton Retirer.
    qty = max(1, qty)

    if qty > item.product.quantity:
        return JsonResponse({'success': False,
                             'error': f'Stock max : {item.product.quantity}'})
    item.quantity = qty
    item.save()
    cart = _get_or_create_cart(request.user)
    return JsonResponse({
        'success':    True,
        'subtotal':   float(item.subtotal),
        'cart_total': float(cart.total),
        'cart_count': cart.items_count,
    })


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    item.delete()
    messages.success(request, "Article retiré du panier.")
    return redirect('orders:cart')


# ──────────────────────────────────────────────────────────────
# EXPIRY CHECK API (AJAX — appelé depuis le checkout)
# ──────────────────────────────────────────────────────────────
@login_required
def check_expiry_api(request):
    """
    GET ?wilaya=16&method=standard
    Retourne les conflits expiry/livraison pour le panier actuel.
    """
    wilaya  = request.GET.get('wilaya', '').strip()
    method  = request.GET.get('method', 'standard').strip()
    cart    = _get_or_create_cart(request.user)
    items   = cart.cart_items.select_related('product').all()
    conflicts = _check_expiry_conflicts(items, wilaya, method)
    return JsonResponse({
        'has_conflicts': len(conflicts) > 0,
        'conflicts': [
            {
                'name':          c['name'],
                'expiry':        c['expiry'],
                'remaining_days': c['remaining'],
                'delivery_days': c['delivery_days'],
            }
            for c in conflicts
        ],
    })


# ──────────────────────────────────────────────────────────────
# CHECKOUT
# ──────────────────────────────────────────────────────────────
@login_required
def checkout(request):
    if not request.user.is_customer:
        return redirect('dashboard:index')
    cart  = _get_or_create_cart(request.user)
    items = cart.cart_items.select_related('product__store').prefetch_related('product__images')
    if not items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect('orders:cart')

    virtual_card = None
    try:
        virtual_card = request.user.virtual_card
    except Exception:
        pass

    ctx = {
        'cart':         cart,
        'items':        items,
        'virtual_card': virtual_card,
        'wilayas':      WILAYA_CHOICES,
        'user_wilaya':  request.user.wilaya,
        'user_address': request.user.address,
        'user_phone':   request.user.phone,
        'expiry_conflicts': [],
    }

    if request.method == 'POST':
        pm      = request.POST.get('payment_method', 'cod')
        wilaya  = request.POST.get('delivery_wilaya', '').strip()
        address = request.POST.get('delivery_address', '').strip()
        phone   = request.POST.get('delivery_phone', '').strip()
        dmethod = request.POST.get('delivery_method', 'standard')
        force   = request.POST.get('force_order') == '1'  # bypass expiry warning

        # ── Validation basique ───────────────────────────────
        errors = []
        if not wilaya:  errors.append("Sélectionnez votre wilaya.")
        if not address: errors.append("Entrez votre adresse de livraison.")
        if not phone:   errors.append("Entrez votre numéro de téléphone.")
        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'orders/checkout.html', ctx)

        # ── Vérification expiry / délai livraison ────────────
        if not force:
            conflicts = _check_expiry_conflicts(items, wilaya, dmethod)
            if conflicts:
                ctx.update({
                    'expiry_conflicts': conflicts,
                    'selected_wilaya':  wilaya,
                    'selected_address': address,
                    'selected_phone':   phone,
                    'selected_method':  dmethod,
                    'selected_payment': pm,
                })
                return render(request, 'orders/checkout.html', ctx)

        # ── Paiement carte virtuelle ─────────────────────────
        if pm == 'virtual_card':
            if not virtual_card or not virtual_card.is_active:
                messages.error(request, "Carte virtuelle inactive.")
                return render(request, 'orders/checkout.html', ctx)
            if virtual_card.balance < cart.total:
                messages.error(request,
                    f"Solde insuffisant ({virtual_card.balance:.0f} DA). "
                    f"Total : {cart.total:.0f} DA.")
                return render(request, 'orders/checkout.html', ctx)

        # ── Calcul livraison ─────────────────────────────────
        from delivery.models import get_delivery_cost
        delivery_info = get_delivery_cost(wilaya, dmethod)
        dcost = delivery_info['price']

        # ── Création commande ────────────────────────────────
        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                delivery_wilaya=wilaya,
                delivery_address=address,
                delivery_phone=phone,
                delivery_method=dmethod,
                status='pending',
            )
            # Check for session-based negotiated price
            nego_deal = request.session.get('nego_deal')
            nego_product_pk = int(nego_deal['product_pk']) if nego_deal else None
            nego_price = Decimal(nego_deal['price']) if nego_deal else None

            for ci in items:
                # If this product has a negotiated price, use it
                if nego_product_pk and ci.product.pk == nego_product_pk and nego_price:
                    item_price = nego_price
                else:
                    item_price = ci.product.current_price
                OrderItem.objects.create(
                    order=order,
                    product=ci.product,
                    quantity=ci.quantity,
                    unit_price=item_price,
                )
                ci.product.quantity    -= ci.quantity
                ci.product.sales_count += ci.quantity
                if ci.product.quantity == 0:
                    ci.product.status = 'sold_out'
                ci.product.save(update_fields=['quantity', 'sales_count', 'status'])
                try:
                    ci.product.store.total_sales += ci.quantity
                    ci.product.store.save(update_fields=['total_sales'])
                except Exception:
                    pass

            order.calculate_total()
            order.total_amount = order.total_amount + dcost
            order.save(update_fields=['total_amount'])

            from payments.models import Payment
            payment = Payment.objects.create(
                user=request.user,
                order=order,
                method=pm,
                amount=order.total_amount,
                status='completed' if pm == 'virtual_card' else 'pending',
            )

            if pm == 'virtual_card':
                virtual_card.balance -= order.total_amount
                virtual_card.save(update_fields=['balance'])

            order.status = 'confirmed'
            order.save(update_fields=['status'])
            cart.cart_items.all().delete()

            # ── Link negotiation if from a deal ──────────────
            if nego_deal:
                try:
                    from negotiations.models import Negotiation
                    nego_obj = Negotiation.objects.get(
                        pk=int(nego_deal['nego_pk']),
                        buyer=request.user,
                        status='accepted'
                    )
                    nego_obj.mark_ordered(order)
                except Exception:
                    pass
                request.session.pop('nego_deal', None)

            # ── Notifications temps réel ─────────────────────
            _notify_vendors(order)
            _notify_buyer_confirmed(order)

        messages.success(request,
            f"🎉 Commande #{order.order_number} confirmée ! Merci pour votre achat.")
        return redirect('orders:confirmation', order_number=order.order_number)

    return render(request, 'orders/checkout.html', ctx)


# ──────────────────────────────────────────────────────────────
# VENDOR — Confirmer / Annuler commande
# ──────────────────────────────────────────────────────────────
@login_required
@require_POST
def vendor_update_order(request, order_number):
    """
    Permet au vendeur de confirmer ou annuler une commande.
    POST data: action = 'confirm' | 'cancel'
    Envoie une notification en temps réel à l'acheteur.
    """
    if not request.user.is_vendor:
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    order  = get_object_or_404(Order, order_number=order_number)
    # Vérifier que cette commande contient au moins un produit du vendeur
    has_products = order.items.filter(
        product__store__owner=request.user
    ).exists()
    if not has_products:
        return JsonResponse({'error': 'Commande introuvable'}, status=404)

    action = request.POST.get('action', '')
    from notifications.models import send_notification

    if action == 'confirm' and order.status in ('pending',):
        order.status = 'confirmed'
        order.save(update_fields=['status'])
        send_notification(
            recipient=order.customer,
            notif_type='order_confirmed',
            title=f'✅ Commande #{order.order_number} confirmée !',
            body=(
                f'Votre commande a été confirmée par '
                f'{request.user.store.name if hasattr(request.user, "store") else "le vendeur"}. '
                f'Préparation en cours.'
            ),
            link=f'/orders/{order.order_number}/',
        )
        return JsonResponse({'ok': True, 'status': 'confirmed',
                             'label': 'Confirmée', 'msg': 'Commande confirmée !'})

    elif action == 'cancel' and order.status in ('pending', 'confirmed'):
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        # Rembourser si paiement par carte virtuelle
        try:
            pay = order.payment
            if pay.method == 'virtual_card' and pay.status == 'completed':
                vc = order.customer.virtual_card
                vc.balance += order.total_amount
                vc.save(update_fields=['balance'])
                pay.status = 'refunded'
                pay.save(update_fields=['status'])
        except Exception:
            pass
        send_notification(
            recipient=order.customer,
            notif_type='order_cancelled',
            title=f'❌ Commande #{order.order_number} annulée',
            body=(
                f'Votre commande a été annulée par le vendeur. '
                f'Montant remboursé si paiement en ligne.'
            ),
            link=f'/orders/{order.order_number}/',
        )
        return JsonResponse({'ok': True, 'status': 'cancelled',
                             'label': 'Annulée', 'msg': 'Commande annulée.'})

    return JsonResponse({'error': f'Action invalide ou statut incompatible ({order.status})'}, status=400)


# ──────────────────────────────────────────────────────────────
# ORDER VIEWS
# ──────────────────────────────────────────────────────────────
@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    payment = None
    try:
        payment = order.payment
    except Exception:
        pass
    return render(request, 'orders/confirmation.html', {'order': order, 'payment': payment})


@login_required
def order_list(request):
    orders = (Order.objects
              .filter(customer=request.user)
              .prefetch_related('items__product__images', 'items__product__category')
              .order_by('-created_at'))
    return render(request, 'orders/list.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items__product__images', 'items__product__store'
        ),
        order_number=order_number,
        customer=request.user,
    )
    payment = None
    try:
        payment = order.payment
    except Exception:
        pass
    return render(request, 'orders/detail.html', {'order': order, 'payment': payment})


@login_required
def order_cancel(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    if order.status not in ('pending', 'confirmed'):
        messages.error(request, "Cette commande ne peut plus être annulée.")
        return redirect('orders:detail', order_number=order_number)
    if request.method == 'POST':
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        try:
            pay = order.payment
            if pay.method == 'virtual_card' and pay.status == 'completed':
                vc = request.user.virtual_card
                vc.balance += order.total_amount
                vc.save(update_fields=['balance'])
                pay.status = 'refunded'
                pay.save(update_fields=['status'])
                messages.success(request,
                    f"✅ Commande annulée. {order.total_amount:.0f} DA remboursés.")
            else:
                messages.success(request, "✅ Commande annulée.")
        except Exception:
            messages.success(request, "✅ Commande annulée.")
        return redirect('orders:list')
    return render(request, 'orders/cancel_confirm.html', {'order': order})
