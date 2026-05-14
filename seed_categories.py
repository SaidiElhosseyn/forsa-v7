from django.core.management.base import BaseCommand
from products.models import Category

CATEGORIES = [
    ('💄', 'Cosmétiques & Beauté',  'cosmetiques-beaute',  1),
    ('💊', 'Santé & Pharmacie',     'sante-pharmacie',     2),
    ('🧴', 'Hygiène & Soins',       'hygiene-soins',       3),
    ('🐾', 'Animalerie',            'animalerie',          4),
    ('👗', 'Mode & Textile',        'mode-textile',        5),
    ('🌿', 'Bio & Naturel',         'bio-naturel',         6),
    ('🏋️', 'Sport & Bien-être',    'sport-bien-etre',     7),
    ('🛒', 'Alimentation sèche',    'alimentation-seche',  8),
    ('🍫', 'Confiseries & Snacks',  'confiseries-snacks',  9),
    ('🧃', 'Boissons',              'boissons',            10),
    ('🥛', 'Produits laitiers',     'produits-laitiers',   11),
]

class Command(BaseCommand):
    help = 'Seed FORSA product categories (idempotent — safe to run multiple times)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete all existing categories before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            n = Category.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Deleted {n} existing categories.'))

        created = updated = 0
        for icon, name, slug, order in CATEGORIES:
            obj, was_created = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    'name':      name,
                    'icon':      icon,
                    'order':     order,
                    'is_active': True,
                }
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Créée  : {icon} {name}'))
            else:
                updated += 1
                self.stdout.write(f'  ↻  Mise à jour : {icon} {name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Terminé — {created} créée(s), {updated} mise(s) à jour.'
            )
        )
        self.stdout.write('Lancer : python manage.py seed_categories')
