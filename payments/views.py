
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Payment
@login_required
def virtual_card_view(request):
    try: card = request.user.virtual_card
    except Exception: card = None
    payments = Payment.objects.filter(user=request.user, method="virtual_card").order_by("-created_at")[:10]
    return render(request,"payments/virtual_card.html",{"card":card,"payments":payments})
@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request,"payments/history.html",{"payments":payments})
