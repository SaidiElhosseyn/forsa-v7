"""
python manage.py send_expiry_alerts
Run daily via cron to alert vendors of products expiring soon.
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Send expiry and low-stock alerts to vendors'

    def handle(self, *args, **options):
        from products.models import Product
        from notifications.models import send_notification

        today = timezone.now().date()
        thresholds = [3, 7, 14]
        expiry_count = 0
        stock_count = 0

        for days in thresholds:
            deadline = today + timedelta(days=days)
            products = Product.objects.filter(
                status='active',
                expiry_date=deadline,
            ).select_related('store__owner')

            for p in products:
                vendor = p.store.owner
                send_notification(
                    recipient=vendor,
                    notif_type='expiry_alert',
                    title=f'Alerte peremption — {p.name[:40]}',
                    body=f'Ce produit expire dans {days} jour(s) ({deadline.strftime("%d/%m/%Y")}). Pensez a le mettre en promotion.',
                    link=f'/products/{p.slug}/',
                )
                expiry_count += 1

        # Low-stock alert: quantity <= 5
        low_stock = Product.objects.filter(
            status='active', quantity__lte=5, quantity__gt=0
        ).select_related('store__owner')

        for p in low_stock:
            vendor = p.store.owner
            send_notification(
                recipient=vendor,
                notif_type='stock_warning',
                title=f'Stock faible — {p.name[:40]}',
                body=f'Il ne reste que {p.quantity} {p.unit}(s) en stock.',
                link=f'/products/{p.slug}/',
            )
            stock_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'[OK] {expiry_count} expiry alerts + {stock_count} stock warnings sent.'
        ))
