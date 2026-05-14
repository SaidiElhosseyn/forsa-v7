from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import LoginForm, CustomerRegisterForm, VendorRegisterForm, ProfileUpdateForm, StyledPasswordChangeForm


def _notify_admins_new_registration(user):
    """Notify all admin users when a new user registers."""
    try:
        from .models import User
        from notifications.models import send_notification
        role_label = 'vendeur' if user.role == 'vendor' else 'acheteur'
        admins = User.objects.filter(role='admin')
        for admin in admins:
            send_notification(
                recipient=admin,
                notif_type='new_registration',
                title=f'Nouvelle inscription — {role_label}',
                body=f'{user.get_full_name() or user.username} vient de créer un compte {role_label}.',
                link='/dashboard/admin/',
            )
    except Exception:
        pass


# ── Login ───────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name or user.username} ! 🌿")
            next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard:index'
            return redirect(next_url)
        else:
            # Non-field errors are already in form — no extra message needed
            pass
    return render(request, 'accounts/login.html', {'form': form})


# ── Logout ──────────────────────────────────────────────────
def logout_view(request):
    name = request.user.first_name or request.user.username
    logout(request)
    messages.info(request, f"À bientôt, {name} !")
    return redirect('home')


# ── Register — choice ───────────────────────────────────────
def register_choice(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return render(request, 'accounts/register_choice.html')


# ── Register — Customer ─────────────────────────────────────
def register_customer(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = CustomerRegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé ! Votre carte virtuelle de 100 000 DA est prête.")
            _notify_admins_new_registration(user)
            return redirect('dashboard:customer')
    return render(request, 'accounts/register_customer.html', {'form': form})


# ── Register — Vendor ───────────────────────────────────────
def register_vendor(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = VendorRegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte vendeur créé ! Créez votre boutique pour commencer.")
            _notify_admins_new_registration(user)
            return redirect('stores:create')
    return render(request, 'accounts/register_vendor.html', {'form': form})


# ── Profile ─────────────────────────────────────────────────
@login_required
def profile_view(request):
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profil mis à jour avec succès !")
            return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})


# ── Password change ─────────────────────────────────────────
@login_required
def password_change_view(request):
    form = StyledPasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Stay logged in
            messages.success(request, "✅ Mot de passe modifié avec succès !")
            return redirect('accounts:profile')
    return render(request, 'accounts/password_change.html', {'form': form})


# ── Wishlist ─────────────────────────────────────────────────
@login_required
def wishlist_page(request):
    from .models import Wishlist
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    products = (wishlist.products
                .filter(status='active')
                .select_related('store', 'category')
                .prefetch_related('images')
                .order_by('-wishlisted_by__updated_at'))
    return render(request, 'accounts/wishlist.html', {
        'products': products,
        'count': products.count(),
    })


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    from .models import Wishlist
    from products.models import Product
    product = get_object_or_404(Product, pk=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        added = False
        msg = 'Retiré des favoris.'
    else:
        wishlist.products.add(product)
        added = True
        msg = 'Ajouté aux favoris !'
    return JsonResponse({
        'added': added,
        'count': wishlist.products.count(),
        'message': msg,
    })
