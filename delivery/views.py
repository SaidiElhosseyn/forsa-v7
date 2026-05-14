
from django.http import JsonResponse
from .models import get_delivery_cost
def delivery_price(request):
    wilaya = request.GET.get("wilaya","")
    method = request.GET.get("method","standard")
    if not wilaya: return JsonResponse({"error":"wilaya required"},status=400)
    return JsonResponse(get_delivery_cost(wilaya, method))
