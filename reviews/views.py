
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Review
from products.models import Product
@login_required
@require_POST
def add_review(request, slug):
    if not request.user.is_customer:
        messages.error(request,"Seuls les acheteurs peuvent laisser un avis."); return redirect("products:detail",slug=slug)
    product = get_object_or_404(Product, slug=slug)
    r,c = Review.objects.get_or_create(product=product,customer=request.user,
           defaults={"rating":int(request.POST.get("rating",5)),"comment":request.POST.get("comment","")})
    if not c:
        r.rating=int(request.POST.get("rating",5)); r.comment=request.POST.get("comment",""); r.save()
        messages.success(request,"Avis mis à jour !")
    else: messages.success(request,"Avis ajouté !")
    return redirect("products:detail",slug=slug)
