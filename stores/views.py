import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Store
from .forms import StoreForm


# ── helpers ───────────────────────────────────────────────────
def _annotate_stores(qs):
    from django.db.models import Count
    from products.models import Product
    return qs.annotate(
        product_count=Count(
            'products',
            filter=Q(products__status='active', products__quantity__gt=0)
        )
    )


# ── Map / Géolocalisation ─────────────────────────────────────
def store_map(request):
    """
    Page carte interactive Leaflet.js.
    Returns HTML with all geo-located stores + nearest products.
    Also handles AJAX ?format=json to return GeoJSON for the map.
    """
    stores_qs = (Store.objects
                 .filter(status='active')
                 .prefetch_related('products')
                 .select_related('owner'))

    if request.GET.get('format') == 'json':
        # ── GeoJSON endpoint ─────────────────────────────
        features = []
        for s in stores_qs:
            lat = float(s.latitude)  if s.latitude  else None
            lng = float(s.longitude) if s.longitude else None
            # Fallback: derive approximate coords from wilaya
            if lat is None or lng is None:
                lat, lng = _wilaya_coords(s.wilaya)

            # Best product (lowest expiry / highest discount)
            best = (s.products
                    .filter(status='active', quantity__gt=0)
                    .order_by('expiry_date', '-discount_pct')
                    .first())
            features.append({
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [lng, lat]},
                'properties': {
                    'id':          s.pk,
                    'name':        s.name,
                    'wilaya':      s.wilaya,
                    'address':     s.address,
                    'rating':      str(s.rating),
                    'slug':        s.slug,
                    'product_count': s.products.filter(status='active').count(),
                    'best_product': {
                        'name':         best.name,
                        'price':        str(best.current_price),
                        'discount_pct': str(best.discount_pct),
                        'expiry_date':  best.expiry_date.isoformat(),
                        'slug':         best.slug,
                        'icon':         best.category.icon if best.category else '📦',
                    } if best else None,
                },
            })
        return JsonResponse({'type': 'FeatureCollection', 'features': features})

    # Normal page render
    stores = _annotate_stores(stores_qs).order_by('-total_sales')
    return render(request, 'stores/map.html', {'stores': stores})


def _wilaya_coords(code):
    """Approximate centroid coords for each Algerian wilaya (fallback)."""
    COORDS = {
        '01': (27.87, 0.28),  '02': (36.16, 1.33),  '03': (33.8,  2.89),
        '04': (35.93, 7.11),  '05': (35.56, 6.17),  '06': (36.76, 5.08),
        '07': (34.85, 5.73),  '08': (31.62, 2.21),  '09': (36.47, 2.82),
        '10': (36.37, 3.9),   '11': (22.79, 5.52),  '12': (35.41, 8.12),
        '13': (34.87, 1.31),  '14': (35.37, 1.32),  '15': (36.71, 4.05),
        '16': (36.73, 3.08),  '17': (34.67, 3.26),  '18': (36.82, 5.77),
        '19': (36.19, 5.41),  '20': (34.83, 0.15),  '21': (36.9,  6.9),
        '22': (35.19, 0.63),  '23': (36.9,  7.77),  '24': (36.46, 7.43),
        '25': (36.36, 6.61),  '26': (36.27, 2.75),  '27': (35.94, 0.09),
        '28': (35.7,  4.54),  '29': (35.39, 0.14),  '30': (31.95, 5.32),
        '31': (35.7,  -0.63), '32': (33.68, 1.02),  '33': (26.51, 8.48),
        '34': (36.07, 4.77),  '35': (36.76, 3.48),  '36': (36.77, 8.31),
        '37': (27.67, -8.14), '38': (35.6,  1.86),  '39': (33.37, 6.86),
        '40': (35.43, 7.14),  '41': (36.28, 7.96),  '42': (36.59, 2.89),
        '43': (36.45, 6.26),  '44': (36.27, 1.97),  '45': (33.27, 0.31),
        '46': (35.3,  -0.28), '47': (32.49, 3.67),  '48': (35.74, 0.56),
    }
    return COORDS.get(code or '', (28.0, 2.7))


# ── CRUD ──────────────────────────────────────────────────────
@login_required
def store_create(request):
    if not request.user.is_vendor:
        messages.error(request, "Réservé aux vendeurs.")
        return redirect('dashboard:index')
    if hasattr(request.user, 'store'):
        return redirect('stores:my_store')

    form = StoreForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        s = form.save(commit=False)
        s.owner  = request.user
        s.status = 'active'
        s.save()
        messages.success(request, f"🏪 Boutique « {s.name} » créée avec succès !")
        return redirect('stores:my_store')
    return render(request, 'stores/create.html', {'form': form})


@login_required
def store_edit(request):
    store = get_object_or_404(Store, owner=request.user)
    form  = StoreForm(request.POST or None, request.FILES or None, instance=store)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Boutique mise à jour !")
        return redirect('stores:my_store')
    return render(request, 'stores/edit.html', {'form': form, 'store': store})


@login_required
def my_store(request):
    if not request.user.is_vendor:
        return redirect('dashboard:index')
    try:
        store = request.user.store
    except Store.DoesNotExist:
        return redirect('stores:create')

    products = (store.products
                .select_related('category')
                .prefetch_related('images')
                .order_by('expiry_date', '-created_at'))
    return render(request, 'stores/my_store.html', {'store': store, 'products': products})


def store_detail(request, slug):
    store = get_object_or_404(Store, slug=slug)
    if store.status != 'active' and (
        not request.user.is_authenticated or request.user != store.owner
    ):
        from django.http import Http404
        raise Http404
    products = (store.products
                .filter(status='active', quantity__gt=0)
                .select_related('category')
                .prefetch_related('images')
                .order_by('expiry_date'))
    return render(request, 'stores/detail.html', {'store': store, 'products': products})


def stores_list(request):
    stores = (_annotate_stores(
        Store.objects.filter(status='active').select_related('owner')
    ).order_by('-created_at'))
    return render(request, 'stores/list.html', {'stores': stores})
