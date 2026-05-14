from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Product, Category, ProductImage
from .forms import ProductForm


# ──────────────────────────────────────────────────────────────
def apply_discount(product, manual_pct=None):
    """
    Calcule current_price + discount_pct.

    Priorité :
      1. manual_pct (saisi par le vendeur dans le formulaire)
      2. DiscountRule FORSA (selon jours avant expiry)
      3. 0 % si rien ne correspond

    La réduction automatique FORSA s'applique EN PLUS
    de la réduction manuelle : le meilleur % gagne.
    """
    orig = Decimal(str(product.original_price))
    days = (product.expiry_date - timezone.now().date()).days

    # Réduction automatique FORSA
    auto_pct = Decimal('0')
    try:
        from discounts.models import DiscountRule
        for rule in DiscountRule.objects.filter(is_active=True).order_by('days_threshold'):
            if days <= rule.days_threshold:
                auto_pct = Decimal(str(rule.discount_pct))
                break
    except Exception:
        pass

    # Réduction manuelle vendeur
    man_pct = Decimal(str(manual_pct or 0))

    # On prend la plus haute (protège l'acheteur)
    final_pct = max(auto_pct, man_pct)

    product.discount_pct  = final_pct
    product.current_price = round(orig * (1 - final_pct / 100), 2)


# ──────────────────────────────────────────────────────────────
def catalog(request):
    products = (Product.objects
                .filter(status='active', quantity__gt=0)
                .select_related('store', 'category')
                .prefetch_related('images'))

    q        = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    urgency  = request.GET.get('urgency', '').strip()
    sort     = request.GET.get('sort', 'expiry').strip()

    if category:
        products = products.filter(category__slug=category)
    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(store__name__icontains=q)
            | Q(description__icontains=q)
            | Q(category__name__icontains=q)
        )

    today = timezone.now().date()
    if urgency == 'urgent':
        products = products.filter(expiry_date__gte=today,
                                   expiry_date__lte=today + timedelta(days=3))
    elif urgency == 'warning':
        products = products.filter(expiry_date__gt=today + timedelta(days=3),
                                   expiry_date__lte=today + timedelta(days=7))
    elif urgency == 'safe':
        products = products.filter(expiry_date__gt=today + timedelta(days=7))

    sort_map = {
        'expiry':     'expiry_date',
        'price_asc':  'current_price',
        'price_desc': '-current_price',
        'discount':   '-discount_pct',
        'newest':     '-created_at',
    }
    products  = products.order_by(sort_map.get(sort, 'expiry_date'))
    total     = products.count()
    paginator = Paginator(products, 12)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    active_category = None
    if category:
        active_category = Category.objects.filter(slug=category, is_active=True).first()

    return render(request, 'products/catalog.html', {
        'page_obj':        page_obj,
        'categories':      Category.objects.filter(is_active=True).order_by('order'),
        'active_category': active_category,
        'q':        q,
        'category': category,
        'urgency':  urgency,
        'sort':     sort,
        'total':    total,
        'urgency_list': [
            ('',        'Tous les produits',    '#9AB09A'),
            ('urgent',  '🔴 Moins de 3 jours', '#DC2626'),
            ('warning', '🟡 3 à 7 jours',      '#D97706'),
            ('safe',    '🟢 Plus de 7 jours',  '#16A34A'),
        ],
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects
        .select_related('store', 'category')
        .prefetch_related('images', 'reviews__customer'),
        slug=slug, status='active'
    )
    product.views_count += 1
    product.save(update_fields=['views_count'])
    related = (Product.objects
               .filter(category=product.category, status='active', quantity__gt=0)
               .exclude(pk=product.pk)
               .order_by('expiry_date')
               .prefetch_related('images')[:4])
    return render(request, 'products/detail.html', {
        'product': product, 'related': related,
    })


@login_required
def product_create(request):
    if not request.user.is_vendor:
        messages.error(request, "Réservé aux vendeurs.")
        return redirect('dashboard:index')
    if not hasattr(request.user, 'store'):
        messages.info(request, "Créez votre boutique d'abord.")
        return redirect('stores:create')

    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        p = form.save(commit=False)
        p.store = request.user.store
        manual_pct = form.cleaned_data.get('discount_pct') or 0
        apply_discount(p, manual_pct=manual_pct)
        p.save()
        for i, img in enumerate(request.FILES.getlist('images')):
            ProductImage.objects.create(product=p, image=img,
                                        is_primary=(i == 0), order=i)
        messages.success(request, f"✅ Produit « {p.name} » publié ! "
                         f"Prix affiché : {p.current_price:.0f} DA "
                         f"({'−' + str(int(p.discount_pct)) + '%' if p.discount_pct > 0 else 'sans réduction'})")
        return redirect('stores:my_store')
    return render(request, 'products/create.html', {'form': form})


@login_required
def product_edit(request, slug):
    product = get_object_or_404(Product, slug=slug, store__owner=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        p = form.save(commit=False)
        manual_pct = form.cleaned_data.get('discount_pct') or 0
        apply_discount(p, manual_pct=manual_pct)
        p.save()
        messages.success(request, "✅ Produit mis à jour !")
        return redirect('stores:my_store')
    return render(request, 'products/edit.html', {'form': form, 'product': product})


@login_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug, store__owner=request.user)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"🗑️ Produit « {name} » supprimé.")
        return redirect('stores:my_store')
    return render(request, 'products/confirm_delete.html', {'product': product})


def categories_page(request):
    categories = Category.objects.filter(is_active=True).order_by('order')
    q = request.GET.get('q', '').strip()
    selected_cat = request.GET.get('category', '').strip()

    categories_with_products = []
    for cat in categories:
        products = (Product.objects
                    .filter(status='active', quantity__gt=0, category=cat)
                    .select_related('store', 'category')
                    .prefetch_related('images')
                    .order_by('expiry_date'))
        if selected_cat and cat.slug != selected_cat:
            continue
        if q:
            products = products.filter(
                Q(name__icontains=q) | Q(store__name__icontains=q)
            )
        if products.exists():
            categories_with_products.append({
                'category': cat,
                'products': products[:4],
                'total': products.count(),
            })

    return render(request, 'products/categories.html', {
        'categories_with_products': categories_with_products,
        'categories': categories,
        'q': q,
        'selected_cat': selected_cat,
    })


def search_autocomplete(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    products = (Product.objects
                .filter(status='active', quantity__gt=0)
                .filter(Q(name__icontains=q) | Q(store__name__icontains=q) | Q(category__name__icontains=q))
                .select_related('store', 'category')
                .prefetch_related('images')
                .order_by('expiry_date')[:8])
    results = []
    for p in products:
        img = p.images.first()
        results.append({
            'name': p.name,
            'store': p.store.name,
            'category': p.category.name if p.category else '',
            'icon': p.category.icon if p.category else '📦',
            'price': float(p.current_price),
            'discount': float(p.discount_pct),
            'slug': p.slug,
            'image': img.image.url if img else None,
        })
    return JsonResponse({'results': results})
