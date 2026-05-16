from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


def home_view(request):
    from products.models import Product, Category
    from django.utils import timezone
    # Produits mis en avant — réels depuis la DB
    featured = (Product.objects
                .filter(status='active', quantity__gt=0)
                .select_related('store', 'category')
                .prefetch_related('images')
                .order_by('-discount_pct', 'expiry_date')[:8])
    # Urgents (≤3j) — pour la section spéciale
    today = timezone.now().date()
    from datetime import timedelta
    urgent = (Product.objects
              .filter(status='active', quantity__gt=0,
                      expiry_date__gte=today,
                      expiry_date__lte=today + timedelta(days=3))
              .select_related('store','category')
              .prefetch_related('images')
              .order_by('expiry_date')[:4])
    categories = Category.objects.filter(is_active=True).order_by('order')
    return render(request, 'home.html', {
        'featured_products': featured,
        'urgent_products':   urgent,
        'categories':        categories,
        'products_count':    Product.objects.filter(status='active').count(),
    })



def handler404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def handler500_view(request):
    return render(request, 'errors/500.html', status=500)


urlpatterns = [
    path('admin/',         admin.site.urls),
    path('',               home_view,                   name='home'),
    path('accounts/',      include('accounts.urls')),
    path('dashboard/',     include('dashboard.urls')),
    path('stores/',        include('stores.urls')),
    path('products/',      include('products.urls')),
    path('orders/',        include('orders.urls')),
    path('payments/',      include('payments.urls')),
    path('delivery/',      include('delivery.urls')),
    path('reviews/',       include('reviews.urls')),
    path('notifications/', include('notifications.urls')),
    path('negotiations/', include('negotiations.urls')),
]

# Always serve local media (fallback when Cloudinary not configured)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = handler404_view
handler500 = handler500_view
