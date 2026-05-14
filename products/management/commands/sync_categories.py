"""
Usage:
    python manage.py sync_categories

Synchronizes the Category table with the official FORSA list.
- Removes: Bébé & Maternité, Maison & Entretien, Électronique (per spec)
- Creates missing categories
- Preserves existing slugs / products
"""
from django.core.management.base import BaseCommand
from products.models import Category

# ── Official FORSA category list (Bébé, Maison, Électronique REMOVED) ──
FORSA_CATEGORIES = [
    ('cosmetiques-beaute', '💄', 'Cosmétiques & Beauté',  1),
    ('sante-pharmacie',    '💊', 'Santé & Pharmacie',     2),
    ('hygiene-soins',      '🧴', 'Hygiène & Soins',       3),
    ('animalerie',         '🐾', 'Animalerie',            4),
    ('mode-textile',       '👗', 'Mode & Textile',        5),
    ('bio-naturel',        '🌿', 'Bio & Naturel',         6),
    ('sport-bien-etre',    '🏋️', 'Sport & Bien-être',    7),
    ('alimentation-seche', '🛒', 'Alimentation sèche',   8),
    ('confiseries-snacks', '🍫', 'Confiseries & Snacks', 9),
    ('boissons',           '🧃', 'Boissons',             10),
    ('produits-laitiers',  '🥛', 'Produits laitiers',   11),
]

# Slugs to deactivate (no delete — products may still reference them)
REMOVED_SLUGS = ['bebe-maternite', 'maison-entretien', 'electronique']


class Command(BaseCommand):
    help = 'Synchronise les catégories FORSA (supprime Bébé, Maison, Électronique)'

    def add_arguments(self, parser):
        parser.add_argument('--hard-delete', action='store_true',
                            help='Supprimer définitivement les catégories retirées (risqué si produits associés)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Synchronisation des catégories FORSA ===\n'))

        # 1. Deactivate / delete removed categories
        for slug in REMOVED_SLUGS:
            try:
                cat = Category.objects.get(slug=slug)
                if options['hard_delete']:
                    name = cat.name
                    cat.delete()
                    self.stdout.write(self.style.ERROR(f'  🗑  Supprimée : {name}'))
                else:
                    cat.is_active = False
                    cat.save(update_fields=['is_active'])
                    self.stdout.write(self.style.WARNING(f'  ⛔  Désactivée : {cat.name}'))
            except Category.DoesNotExist:
                self.stdout.write(f'  —  Introuvable (déjà absente) : {slug}')

        # 2. Create or update official categories
        for slug, icon, name, order in FORSA_CATEGORIES:
            cat, created = Category.objects.get_or_create(slug=slug)
            cat.icon      = icon
            cat.name      = name
            cat.order     = order
            cat.is_active = True
            cat.save()
            status = '✅ Créée' if created else '🔄 Mise à jour'
            self.stdout.write(f'  {status} : {icon} {name}')

        total = Category.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(f'\n✨ Synchronisation terminée — {total} catégories actives.\n'))
