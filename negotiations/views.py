from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Negotiation
from products.models import Product
from notifications.models import send_notification


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def _notify(recipient, notif_type, title, body, pk):
    send_notification(
        recipient=recipient,
        notif_type=notif_type,
        title=title,
        body=body,
        link=f'/negotiations/{pk}/',
    )


def _expire_old():
    """Marque comme expirées les négociations non répondues."""
    from django.utils import timezone
    Negotiation.objects.filter(
        status__in=('pending', 'counter'),
        expires_at__lt=timezone.now()
    ).update(status='expired')


# ──────────────────────────────────────────────────────────────
# START — Acheteur propose un prix
# ──────────────────────────────────────────────────────────────
@login_required
def start(request, slug):
    if not request.user.is_customer:
        messages.error(request, "Réservé aux acheteurs.")
        return redirect('dashboard:index')

    product = get_object_or_404(Product, slug=slug, status='active', quantity__gt=0)
    vendor  = product.store.owner

    if vendor == request.user:
        messages.error(request, "Vous ne pouvez pas négocier votre propre produit.")
        return redirect('products:detail', slug=slug)

    # Une seule négociation active par produit/acheteur
    existing = Negotiation.objects.filter(
        product=product, buyer=request.user,
        status__in=('pending', 'counter', 'accepted')
    ).first()
    if existing:
        messages.info(request, "Vous avez déjà une négociation active sur ce produit.")
        return redirect('negotiations:detail', pk=existing.pk)

    def _ctx(extra=None):
        min_p = product.current_price * Decimal('0.30')
        max_p = product.current_price * Decimal('0.99')
        ctx = {
            'product':         product,
            'min_price':       min_p,
            'max_price':       max_p,
            'suggested_price': round(float(product.current_price) * 0.80),
            'suggestions':     [(10,'Légère'),(20,'Raisonnable'),(30,'Ambitieuse'),(40,'Agressive')],
        }
        if extra:
            ctx.update(extra)
        return ctx

    if request.method == 'POST':
        raw_price = request.POST.get('buyer_price', '').strip()
        buyer_msg = request.POST.get('buyer_message', '').strip()

        try:
            offered = Decimal(raw_price.replace(',', '.'))
        except (InvalidOperation, ValueError):
            messages.error(request, "Prix invalide.")
            return render(request, 'negotiations/start.html', _ctx({'raw_price': raw_price}))

        min_price = product.current_price * Decimal('0.30')

        if offered < min_price:
            messages.error(
                request,
                f"Offre trop basse. Minimum : {min_price:.0f} DA "
                f"(30% du prix actuel de {product.current_price:.0f} DA)."
            )
            return render(request, 'negotiations/start.html', _ctx({'raw_price': raw_price}))

        if offered >= product.current_price:
            messages.error(request, "Votre offre doit être inférieure au prix actuel.")
            return render(request, 'negotiations/start.html', _ctx({'raw_price': raw_price}))

        nego = Negotiation.objects.create(
            product        = product,
            buyer          = request.user,
            vendor         = vendor,
            original_price = product.current_price,
            buyer_price    = offered,
            buyer_message  = buyer_msg,
            status         = 'pending',
        )

        _notify(
            recipient  = vendor,
            notif_type = 'negotiation_offer',
            title      = f'💬 Nouvelle offre sur « {product.name} »',
            body       = (
                f'{request.user.get_full_name() or request.user.username} vous propose '
                f'{offered:.0f} DA au lieu de {product.current_price:.0f} DA '
                f'(−{nego.buyer_discount_pct:.0f}%).'
                + (f' Message : {buyer_msg}' if buyer_msg else '')
            ),
            pk = nego.pk,
        )

        messages.success(
            request,
            f"✅ Offre de {offered:.0f} DA envoyée ! Réponse attendue dans 24h."
        )
        return redirect('negotiations:detail', pk=nego.pk)

    return render(request, 'negotiations/start.html', _ctx())


# ──────────────────────────────────────────────────────────────
# LIST — Vue acheteur + vendeur
# ──────────────────────────────────────────────────────────────
@login_required
def my_negotiations(request):
    _expire_old()

    if request.user.is_customer:
        negos = (Negotiation.objects
                 .filter(buyer=request.user)
                 .select_related('product', 'product__store', 'vendor')
                 .prefetch_related('product__images')
                 .order_by('-created_at'))
        role = 'buyer'
    elif request.user.is_vendor:
        negos = (Negotiation.objects
                 .filter(vendor=request.user)
                 .select_related('product', 'product__store', 'buyer')
                 .prefetch_related('product__images')
                 .order_by('-created_at'))
        role = 'vendor'
    else:
        return redirect('dashboard:index')

    counts = {
        'pending':  negos.filter(status='pending').count(),
        'counter':  negos.filter(status='counter').count(),
        'accepted': negos.filter(status='accepted').count(),
    }
    return render(request, 'negotiations/list.html', {
        'negos':  negos,
        'role':   role,
        'counts': counts,
    })


# ──────────────────────────────────────────────────────────────
# DETAIL — Timeline / Chat
# ──────────────────────────────────────────────────────────────
@login_required
def detail(request, pk):
    _expire_old()
    nego = get_object_or_404(Negotiation, pk=pk)

    # Access control
    if request.user not in (nego.buyer, nego.vendor):
        messages.error(request, "Accès refusé.")
        return redirect('negotiations:list')

    # Auto-expire
    if nego.is_expired and nego.status in ('pending', 'counter'):
        nego.expire()
        messages.warning(request, "⏰ Cette négociation a expiré.")

    role = 'buyer' if request.user == nego.buyer else 'vendor'
    return render(request, 'negotiations/detail.html', {
        'nego': nego, 'role': role,
    })


# ──────────────────────────────────────────────────────────────
# VENDOR RESPOND — Accepter / Refuser / Contre-offre
# ──────────────────────────────────────────────────────────────
@login_required
@require_POST
def vendor_respond(request, pk):
    nego = get_object_or_404(Negotiation, pk=pk, vendor=request.user)

    if nego.status != 'pending':
        return JsonResponse({'error': f'Statut incorrect : {nego.status}'}, status=400)
    if nego.is_expired:
        nego.expire()
        return JsonResponse({'error': 'Négociation expirée.'}, status=400)

    action         = request.POST.get('action', '')
    vendor_msg     = request.POST.get('vendor_message', '').strip()
    counter_raw    = request.POST.get('counter_price', '').strip()
    counter_msg    = request.POST.get('counter_message', '').strip()

    buyer_name = nego.buyer.get_full_name() or nego.buyer.username

    if action == 'accept':
        nego.vendor_message = vendor_msg
        nego.accept(accepted_price=nego.buyer_price)
        _notify(
            recipient  = nego.buyer,
            notif_type = 'negotiation_accepted',
            title      = f'🎉 Offre acceptée — {nego.product.name}',
            body       = (
                f'Votre offre de {nego.buyer_price:.0f} DA a été acceptée par '
                f'{request.user.get_full_name() or request.user.username} !'
                + (f' Message : {vendor_msg}' if vendor_msg else '')
                + f' Finalisez votre commande maintenant.'
            ),
            pk = nego.pk,
        )
        return JsonResponse({'ok': True, 'new_status': 'accepted',
                             'msg': f'Offre de {buyer_name} acceptée !'})

    elif action == 'reject':
        nego.vendor_message = vendor_msg
        nego.reject()
        _notify(
            recipient  = nego.buyer,
            notif_type = 'negotiation_rejected',
            title      = f'❌ Offre refusée — {nego.product.name}',
            body       = (
                f'Votre offre de {nego.buyer_price:.0f} DA a été refusée.'
                + (f' Raison : {vendor_msg}' if vendor_msg else '')
            ),
            pk = nego.pk,
        )
        return JsonResponse({'ok': True, 'new_status': 'rejected',
                             'msg': f'Offre refusée.'})

    elif action == 'counter':
        try:
            counter = Decimal(counter_raw.replace(',', '.'))
        except (InvalidOperation, ValueError):
            return JsonResponse({'error': 'Prix de contre-offre invalide.'}, status=400)

        if counter <= nego.buyer_price:
            return JsonResponse({
                'error': f'La contre-offre ({counter:.0f} DA) doit être supérieure à l\'offre acheteur ({nego.buyer_price:.0f} DA).'
            }, status=400)
        if counter >= nego.original_price:
            return JsonResponse({
                'error': f'La contre-offre doit être inférieure au prix original ({nego.original_price:.0f} DA).'
            }, status=400)

        nego.counter_price   = counter
        nego.vendor_message  = vendor_msg
        nego.counter_message = counter_msg
        nego.status          = 'counter'
        # Réinitialise l'expiration (24h de plus pour l'acheteur)
        from datetime import timedelta
        nego.expires_at = timezone.now() + timedelta(hours=24)
        nego.save(update_fields=['counter_price', 'vendor_message', 'counter_message',
                                 'status', 'expires_at', 'updated_at'])
        _notify(
            recipient  = nego.buyer,
            notif_type = 'negotiation_counter',
            title      = f'🔄 Contre-offre — {nego.product.name}',
            body       = (
                f'{request.user.get_full_name() or request.user.username} vous propose '
                f'{counter:.0f} DA (vous avez offert {nego.buyer_price:.0f} DA). '
                + (counter_msg if counter_msg else '')
                + ' Vous avez 24h pour répondre.'
            ),
            pk = nego.pk,
        )
        return JsonResponse({'ok': True, 'new_status': 'counter',
                             'msg': f'Contre-offre de {counter:.0f} DA envoyée.'})

    return JsonResponse({'error': 'Action inconnue.'}, status=400)


# ──────────────────────────────────────────────────────────────
# BUYER RESPOND — Accepter ou Refuser la contre-offre
# ──────────────────────────────────────────────────────────────
@login_required
@require_POST
def buyer_respond(request, pk):
    nego = get_object_or_404(Negotiation, pk=pk, buyer=request.user)

    if nego.status != 'counter':
        return JsonResponse({'error': f'Aucune contre-offre active.'}, status=400)
    if nego.is_expired:
        nego.expire()
        return JsonResponse({'error': 'Négociation expirée.'}, status=400)

    action = request.POST.get('action', '')
    buyer_counter_msg = request.POST.get('buyer_counter_message', '').strip()

    if action == 'accept_counter':
        nego.buyer_counter_message = buyer_counter_msg
        nego.accept(accepted_price=nego.counter_price)
        _notify(
            recipient  = nego.vendor,
            notif_type = 'negotiation_accepted',
            title      = f'🎉 Contre-offre acceptée — {nego.product.name}',
            body       = (
                f'{request.user.get_full_name() or request.user.username} a accepté '
                f'votre contre-offre de {nego.counter_price:.0f} DA !'
            ),
            pk = nego.pk,
        )
        return JsonResponse({'ok': True, 'new_status': 'accepted',
                             'msg': f'Contre-offre de {nego.counter_price:.0f} DA acceptée !'})

    elif action == 'reject_counter':
        nego.buyer_counter_message = buyer_counter_msg
        nego.reject()
        _notify(
            recipient  = nego.vendor,
            notif_type = 'negotiation_rejected',
            title      = f'❌ Contre-offre refusée — {nego.product.name}',
            body       = (
                f'{request.user.get_full_name() or request.user.username} a refusé '
                f'votre contre-offre de {nego.counter_price:.0f} DA.'
                + (f' Raison : {buyer_counter_msg}' if buyer_counter_msg else '')
            ),
            pk = nego.pk,
        )
        return JsonResponse({'ok': True, 'new_status': 'rejected',
                             'msg': 'Contre-offre refusée.'})

    return JsonResponse({'error': 'Action inconnue.'}, status=400)


# ──────────────────────────────────────────────────────────────
# CANCEL
# ──────────────────────────────────────────────────────────────
@login_required
@require_POST
def cancel(request, pk):
    nego = get_object_or_404(Negotiation, pk=pk)
    if request.user not in (nego.buyer, nego.vendor):
        return JsonResponse({'error': 'Accès refusé.'}, status=403)
    if nego.status not in ('pending', 'counter'):
        return JsonResponse({'error': f'Impossible d\'annuler (statut : {nego.status}).'}, status=400)

    nego.status = 'cancelled'
    nego.save(update_fields=['status', 'updated_at'])

    # Notify the other party
    other = nego.vendor if request.user == nego.buyer else nego.buyer
    who   = request.user.get_full_name() or request.user.username
    _notify(
        recipient  = other,
        notif_type = 'system',
        title      = f'🚫 Négociation annulée — {nego.product.name}',
        body       = f'{who} a annulé la négociation.',
        pk = nego.pk,
    )
    messages.info(request, "Négociation annulée.")
    return redirect('negotiations:list')


# ──────────────────────────────────────────────────────────────
# ORDER FROM DEAL — Acheteur finalise après acceptation
# ──────────────────────────────────────────────────────────────
@login_required
def create_order_from_deal(request, pk):
    """
    Redirige l'acheteur vers le checkout en pré-remplissant
    le prix négocié. On utilise un panier temporaire.
    """
    nego = get_object_or_404(Negotiation, pk=pk, buyer=request.user)

    if nego.status != 'accepted':
        messages.error(request, "Cette négociation n'est pas encore acceptée.")
        return redirect('negotiations:detail', pk=pk)
    if nego.order:
        messages.info(request, "Une commande existe déjà pour cette négociation.")
        return redirect('orders:detail', order_number=nego.order.order_number)

    # Ajouter au panier au prix négocié
    from orders.models import Cart, CartItem
    from orders.views import _get_or_create_cart

    product = nego.product
    if product.quantity < 1:
        messages.error(request, "Ce produit n'est plus disponible.")
        return redirect('negotiations:detail', pk=pk)

    # Override temporaire du prix (on stocke l'info en session)
    request.session['nego_deal'] = {
        'nego_pk':    pk,
        'product_pk': product.pk,
        'price':      str(nego.final_price),
    }

    # Vider le panier et y mettre UNIQUEMENT ce produit au prix négocié
    cart = _get_or_create_cart(request.user)
    cart.cart_items.all().delete()

    # Créer CartItem avec override de prix (on utilisera la session dans checkout)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    messages.success(
        request,
        f"🎉 Prix négocié : {nego.final_price:.0f} DA "
        f"(au lieu de {nego.original_price:.0f} DA). Finalisez votre commande."
    )
    return redirect('orders:checkout')
