# python manage.py shell < seed_categories.py
from products.models import Category
Category.objects.all().delete()
FORSA_CATEGORIES = [
    ('cosmetiques-beaute', '💄', 'Cosmétiques & Beauté',  1),
    ('sante-pharmacie',    '💊', 'Santé & Pharmacie',     2),
    ('hygiene-soins',      '🧴', 'Hygiène & Soins',       3),
    ('bebe-maternite',     '🍼', 'Bébé & Maternité',      4),
    ('maison-entretien',   '🏠', 'Maison & Entretien',    5),
    ('animalerie',         '🐾', 'Animalerie',             6),
    ('electronique',       '⚡', 'Électronique',           7),
    ('mode-textile',       '👗', 'Mode & Textile',         8),
    ('bio-naturel',        '🌿', 'Bio & Naturel',          9),
    ('sport-bien-etre',    '🏋️', 'Sport & Bien-être',    10),
    ('alimentation-seche', '🛒', 'Alimentation sèche',   11),
    ('confiseries-snacks', '🍫', 'Confiseries & Snacks', 12),
    ('boissons',           '🧃', 'Boissons',              13),
    ('produits-laitiers',  '🥛', 'Produits laitiers',    14),
]
for slug, icon, name, order in FORSA_CATEGORIES:
    Category.objects.create(slug=slug, icon=icon, name=name, order=order)
    print(f'✅ {icon} {name}')
print(f'\n🎉 {Category.objects.count()} catégories FORSA créées!')
