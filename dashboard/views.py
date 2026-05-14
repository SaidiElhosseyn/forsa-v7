
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import json

@login_required
def dashboard_index(request):
    u = request.user
    if u.is_admin_user: return redirect("dashboard:admin")
    if u.is_vendor:     return redirect("dashboard:vendor")
    return redirect("dashboard:customer")

@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user: return redirect("dashboard:index")
    from accounts.models import User
    from products.models import Product
    from orders.models import Order
    from stores.models import Store
    from negotiations.models import Negotiation

    today = timezone.now().date()
    month = today.replace(day=1)

    # Revenue & orders this month
    rev = Order.objects.filter(
        created_at__date__gte=month, status__in=["confirmed","delivered"]
    ).aggregate(t=Sum("total_amount"))["t"] or 0

    # 7-day chart data
    labels=[]; reg_data=[]; sales_data=[]
    for i in range(6,-1,-1):
        day = today - timedelta(days=i)
        labels.append(day.strftime("%d/%m"))
        reg_data.append(User.objects.filter(date_joined__date=day).count())
        sales_data.append(float(
            Order.objects.filter(created_at__date=day, status__in=["confirmed","delivered"])
            .aggregate(t=Sum("total_amount"))["t"] or 0
        ))

    # Order status counts
    sc = {
        "pending":   Order.objects.filter(status="pending").count(),
        "confirmed": Order.objects.filter(status="confirmed").count(),
        "delivered": Order.objects.filter(status="delivered").count(),
        "cancelled": Order.objects.filter(status="cancelled").count(),
    }

    # Top stores by product count
    top_stores = Store.objects.annotate(
        prod_count=Count("products")
    ).order_by("-prod_count")[:5]

    return render(request, "dashboard/admin.html", {
        # Users
        "total_users":     User.objects.count(),
        "total_vendors":   User.objects.filter(role="vendor").count(),
        "total_customers": User.objects.filter(role="customer").count(),
        # Products
        "total_products":  Product.objects.filter(status="active").count(),
        "expiring_soon":   Product.objects.filter(status="active", expiry_date__lte=today+timedelta(days=3)).count(),
        # Stores
        "total_stores":    Store.objects.filter(status="active").count(),
        # Orders
        "total_orders":    Order.objects.count(),
        "pending_orders":  sc["pending"],
        "confirmed_orders": sc["confirmed"],
        "delivered_orders": sc["delivered"],
        "cancelled_orders": sc["cancelled"],
        "orders_count_month": Order.objects.filter(created_at__date__gte=month).count(),
        "revenue_month":   rev,
        # Negotiations
        "pending_negos":   Negotiation.objects.filter(status="pending").count(),
        # Tables
        "recent_orders":   Order.objects.select_related("customer").order_by("-created_at")[:8],
        "recent_users":    User.objects.order_by("-date_joined")[:8],
        "top_stores":      top_stores,
        # Charts
        "labels":        json.dumps(labels),
        "reg_data":      json.dumps(reg_data),
        "sales_data":    json.dumps(sales_data),
        "status_counts": json.dumps(list(sc.values())),
    })

@login_required
def vendor_dashboard(request):
    if not request.user.is_vendor: return redirect("dashboard:index")
    from orders.models import Order
    today = timezone.now().date()
    month = today.replace(day=1)
    ctx   = {}
    if not hasattr(request.user,"store"):
        return render(request,"dashboard/vendor.html",ctx)
    store = request.user.store
    store_orders = Order.objects.filter(items__product__store=store).distinct()
    rev   = store_orders.filter(created_at__date__gte=month,status__in=["confirmed","delivered"]).aggregate(t=Sum("total_amount"))["t"] or 0
    labels=[]; sales_d=[]; orders_d=[]
    for i in range(6,-1,-1):
        day = today - timedelta(days=i)
        labels.append(day.strftime("%d/%m"))
        do = store_orders.filter(created_at__date=day,status__in=["confirmed","delivered"])
        sales_d.append(float(do.aggregate(t=Sum("total_amount"))["t"] or 0))
        orders_d.append(do.count())
    from negotiations.models import Negotiation
    pending_negos = Negotiation.objects.filter(vendor=request.user, status='pending').count()
    ctx = {"store":store,"products_active":store.products.filter(status="active").count(),
           "expiring_soon":store.products.filter(status="active",expiry_date__lte=today+timedelta(days=3)).count(),
           "pending_negos": pending_negos,
           "revenue_month":rev,"orders_month":store_orders.filter(created_at__date__gte=month).count(),
           "top_products":store.products.order_by("-sales_count")[:5],
           "expiring_products":store.products.filter(status="active",expiry_date__lte=today+timedelta(days=7)).order_by("expiry_date")[:5],
           "recent_orders":store_orders.select_related("customer").order_by("-created_at")[:6],
           "labels":json.dumps(labels),"sales_data":json.dumps(sales_d),"orders_data":json.dumps(orders_d)}
    return render(request,"dashboard/vendor.html",ctx)

@login_required
def customer_dashboard(request):
    if not request.user.is_customer: return redirect("dashboard:index")
    from orders.models import Order
    from products.models import Product
    orders = Order.objects.filter(customer=request.user)
    spent  = orders.filter(status__in=["confirmed","delivered"]).aggregate(t=Sum("total_amount"))["t"] or 0
    savings = sum(float(item.product.original_price - item.unit_price)*item.quantity
                  for order in orders.filter(status__in=["confirmed","delivered"])
                  for item in order.items.all())
    vc = None
    try: vc = request.user.virtual_card
    except Exception: pass
    from negotiations.models import Negotiation
    active_negos = Negotiation.objects.filter(
        buyer=request.user, status__in=('pending','counter','accepted')
    ).count()
    return render(request,"dashboard/customer.html",{
        "orders_count":orders.count(),"total_spent":spent,"total_savings":savings,
        "active_negos": active_negos,
        "recent_orders":orders.order_by("-created_at")[:5],
        "recommended":Product.objects.filter(status="active",quantity__gt=0).order_by("expiry_date")[:8],
        "virtual_card":vc,
    })


@login_required
def vendor_revenue(request):
    """Revenus détaillés du vendeur — tableau mensuel des 6 derniers mois."""
    if not request.user.is_vendor:
        return redirect('dashboard:index')
    from orders.models import Order
    from django.db.models import Sum
    from datetime import timedelta
    today = timezone.now().date()
    months_data = []
    for m in range(5, -1, -1):
        # Premier jour du mois (today - m mois)
        first = (today.replace(day=1) - timedelta(days=m*28)).replace(day=1)
        if m > 0:
            last = (first + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            last = today
        qs = (Order.objects
              .filter(items__product__store__owner=request.user,
                      status__in=['confirmed', 'delivered'],
                      created_at__date__gte=first,
                      created_at__date__lte=last)
              .distinct())
        rev = qs.aggregate(t=Sum('total_amount'))['t'] or 0
        months_data.append({
            'label':  first.strftime('%b %Y'),
            'revenue': float(rev),
            'orders':  qs.count(),
        })
    return render(request, 'dashboard/vendor_revenue.html', {
        'months': months_data,
        'total':  sum(m['revenue'] for m in months_data),
    })


@login_required
def vendor_stats(request):
    """Statistiques produits — vues, ventes, taux de conversion."""
    if not request.user.is_vendor:
        return redirect('dashboard:index')
    if not hasattr(request.user, 'store'):
        return redirect('stores:create')
    from products.models import Product
    products = (Product.objects
                .filter(store=request.user.store)
                .order_by('-views_count')[:20])
    return render(request, 'dashboard/vendor_stats.html', {
        'products': products,
        'store':    request.user.store,
    })
