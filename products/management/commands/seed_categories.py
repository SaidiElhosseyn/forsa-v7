from django.core.management.base import BaseCommand
from products.models import Category

CATEGORIES = [
    ('🛒', 'Supermarché / Alimentation', 'supermarche',      1),
    ('💄', 'Cosmétique',                 'cosmetique',        2),
    ('💊', 'Pharmacie',                  'pharmacie',         3),
    ('🧴', 'Parapharmacie',              'parapharmacie',     4),
    ('🎂', 'Gâteaux & Emballage',        'gateaux-emballage', 5),
]

class Command(BaseCommand):
    help = 'Seed FORSA product categories — 5 categories (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help='Delete all existing categories before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            n = Category.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Deleted {n} existing categories.'))

        created = updated = 0
        for icon, name, slug, order in CATEGORIES:
            _, was_created = Category.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'order': order, 'is_active': True}
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  [+] {name}'))
            else:
                updated += 1
                self.stdout.write(f'  [=] {name}')

        self.stdout.write(self.style.SUCCESS(
            f'\n[OK] {created} creee(s), {updated} mise(s) a jour.'
        ))
