"""
python manage.py seed_data
Creates 8 stores + 48 products with real images downloaded from the web.
Safe to run multiple times (skips existing slugs).
"""
import io
import uuid
import urllib.request
import urllib.error
import urllib.parse
from datetime import date, timedelta
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from accounts.models import User
from stores.models import Store
from products.models import Category, Product, ProductImage


# ── Algerian city GPS ────────────────────────────────────────
CITIES = {
    '16': ('Alger',        36.7538,  3.0588),
    '31': ('Oran',         35.6969, -0.6331),
    '25': ('Constantine',  36.3650,  6.6147),
    '09': ('Blida',        36.4700,  2.8300),
    '19': ('Sétif',        36.1899,  5.4122),
    '13': ('Tlemcen',      34.8782, -1.3150),
    '23': ('Annaba',       36.9000,  7.7667),
    '06': ('Béjaïa',       36.7519,  5.0567),
}


def download_image(url, timeout=12):
    """Download an image from a URL and return ContentFile or None."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return ContentFile(data) if data else None
    except Exception as e:
        import sys
        print(f"      download error: {e}", file=sys.stderr)
        return None


def picsum(seed, w=400, h=400):
    """Deterministic image from picsum.photos."""
    return f"https://picsum.photos/seed/{seed}/{w}/{h}"


def loremflickr(keyword, seed, w=400, h=400):
    """Category-relevant image from loremflickr."""
    kw = urllib.parse.quote(keyword, safe='')
    return f"https://loremflickr.com/{w}/{h}/{kw}?lock={seed}"


# ──────────────────────────────────────────────────────────────
STORES_DATA = [
    {
        'username':    'pharma_amine',
        'password':    'Forsa2025!',
        'first_name':  'Amine',
        'last_name':   'Boudiaf',
        'email':       'amine.boudiaf@pharma-amine.dz',
        'wilaya':      '16',
        'name':        'Pharmacie El Amine',
        'description': 'Votre pharmacie de confiance à Alger. Médicaments, compléments alimentaires, produits de parapharmacie et hygiène à prix réduits. Fondée en 2010, nous servons plus de 500 clients par semaine.',
        'phone':       '0555 12 34 56',
        'address':     '12 Rue Didouche Mourad, Alger-Centre',
        'rating':      Decimal('4.8'),
        'logo_kw':     'pharmacy',
        'banner_kw':   'medicine',
        'logo_seed':   101,
        'banner_seed': 201,
    },
    {
        'username':    'beauty_plus_oran',
        'password':   'Forsa2025!',
        'first_name': 'Nadia',
        'last_name':  'Khelifi',
        'email':      'nadia.khelifi@beautyplus.dz',
        'wilaya':     '31',
        'name':       'Beauty Plus Oran',
        'description': 'Spécialiste beauté & cosmétiques à Oran. Parfums, soins visage et corps, maquillage des meilleures marques (L\'Oréal, Garnier, Nivea, Dove) à des prix défiant toute concurrence. Produits authentiques garantis.',
        'phone':      '0556 78 90 12',
        'address':    '45 Boulevard Millenium, Oran',
        'rating':     Decimal('4.6'),
        'logo_kw':    'beauty',
        'banner_kw':  'cosmetics',
        'logo_seed':  102,
        'banner_seed':202,
    },
    {
        'username':   'bionature_constantine',
        'password':  'Forsa2025!',
        'first_name':'Salim',
        'last_name': 'Merabet',
        'email':     'salim.merabet@bionature.dz',
        'wilaya':    '25',
        'name':      'BioNature Constantine',
        'description':'Boutique spécialisée en produits biologiques et naturels à Constantine. Huiles essentielles, compléments naturels, tisanes, cosmétiques bio certifiés. Nous croyons en une consommation saine et responsable.',
        'phone':     '0557 23 45 67',
        'address':   '8 Rue Larbi Ben M\'hidi, Constantine',
        'rating':    Decimal('4.7'),
        'logo_kw':   'organic',
        'banner_kw': 'nature',
        'logo_seed': 103,
        'banner_seed':203,
    },
    {
        'username':   'sportzone_blida',
        'password':  'Forsa2025!',
        'first_name':'Karim',
        'last_name': 'Hadj',
        'email':     'karim.hadj@sportzone.dz',
        'wilaya':    '09',
        'name':      'SportZone Blida',
        'description':'Équipements sportifs, nutrition et vêtements de sport à Blida. Protéines, barres énergétiques, boissons sportives et accessoires fitness à prix réduits. Partenaire officiel de plusieurs clubs sportifs algériens.',
        'phone':     '0550 34 56 78',
        'address':   '23 Avenue de l\'Indépendance, Blida',
        'rating':    Decimal('4.5'),
        'logo_kw':   'sport',
        'banner_kw': 'fitness',
        'logo_seed': 104,
        'banner_seed':204,
    },
    {
        'username':   'saveurs_setif',
        'password':  'Forsa2025!',
        'first_name':'Fatima',
        'last_name': 'Benali',
        'email':     'fatima.benali@saveurs-setif.dz',
        'wilaya':    '19',
        'name':      'Les Saveurs de Sétif',
        'description':'Épicerie fine et produits alimentaires de qualité à Sétif. Confiseries, biscuits, chocolats, conserves et produits laitiers. Sélection rigoureuse de produits locaux et importés pour les amateurs de bonne table.',
        'phone':     '0553 45 67 89',
        'address':   '17 Rue 8 Mai 1945, Sétif',
        'rating':    Decimal('4.9'),
        'logo_kw':   'food',
        'banner_kw': 'grocery',
        'logo_seed': 105,
        'banner_seed':205,
    },
    {
        'username':   'cave_tlemcen',
        'password':  'Forsa2025!',
        'first_name':'Mohammed',
        'last_name': 'Ziani',
        'email':     'm.ziani@cave-saveurs.dz',
        'wilaya':    '13',
        'name':      'Cave des Saveurs',
        'description':'Spécialiste en boissons et confiseries à Tlemcen. Jus de fruits, boissons gazeuses, eaux minérales, tisanes et thés fins. Importateur direct garantissant fraîcheur et authenticité à des prix imbattables.',
        'phone':     '0554 56 78 90',
        'address':   '5 Rue Khaldi Abdelkader, Tlemcen',
        'rating':    Decimal('4.4'),
        'logo_kw':   'drinks',
        'banner_kw': 'beverages',
        'logo_seed': 106,
        'banner_seed':206,
    },
    {
        'username':   'bebe_confort_annaba',
        'password':  'Forsa2025!',
        'first_name':'Samira',
        'last_name': 'Touati',
        'email':     'samira.touati@bebeconfort.dz',
        'wilaya':    '23',
        'name':      'BébéConfort DZ',
        'description':'Tout pour bébé et la maternité à Annaba. Produits de soin bébé, couches, laits maternisés, jouets éducatifs et vêtements nouveau-nés. Conseils personnalisés par notre équipe de puéricultrices diplômées.',
        'phone':     '0558 67 89 01',
        'address':   '31 Boulevard du 1er Novembre, Annaba',
        'rating':    Decimal('4.8'),
        'logo_kw':   'baby',
        'banner_kw': 'nursery',
        'logo_seed': 107,
        'banner_seed':207,
    },
    {
        'username':   'hygiene_pro_bejaia',
        'password':  'Forsa2025!',
        'first_name':'Rachid',
        'last_name': 'Aoudia',
        'email':     'rachid.aoudia@hygiene-pro.dz',
        'wilaya':    '06',
        'name':      'HygiènePro Béjaïa',
        'description':'Grossiste et détaillant en produits d\'hygiène et d\'entretien à Béjaïa. Détergents, désinfectants, produits de nettoyage professionnels et ménagers. Livraison rapide dans toute la wilaya de Béjaïa.',
        'phone':     '0559 78 90 12',
        'address':   '9 Rue Krim Belkacem, Béjaïa',
        'rating':    Decimal('4.3'),
        'logo_kw':   'cleaning',
        'banner_kw': 'hygiene',
        'logo_seed': 108,
        'banner_seed':208,
    },
]


# ── Products per store ────────────────────────────────────────
PRODUCTS_DATA = {
    'pharma_amine': [
        {
            'name': 'Doliprane 1000mg — boîte 8 comprimés',
            'category': 'sante-pharmacie',
            'original': 320, 'discount': 35,
            'expiry_days': 45,
            'qty': 120, 'unit': 'boîte',
            'weight': 80,
            'description': 'Paracétamol 1000mg, antalgique et antipyrétique. Soulage les douleurs légères à modérées et la fièvre. Boîte de 8 comprimés pelliculés sécables. À conserver à l\'abri de l\'humidité.',
            'img_kw': 'medicine', 'img_seed': 1001,
        },
        {
            'name': 'Vitamines C 500mg — tube 20 comprimés effervescents',
            'category': 'sante-pharmacie',
            'original': 450, 'discount': 40,
            'expiry_days': 60,
            'qty': 85, 'unit': 'tube',
            'weight': 120,
            'description': 'Complément alimentaire riche en vitamine C. Renforce les défenses immunitaires, réduit la fatigue. Goût orange. Sans colorants artificiels. Tube de 20 comprimés effervescents.',
            'img_kw': 'vitamin', 'img_seed': 1002,
        },
        {
            'name': 'Crème hydratante Nivea Soft 200ml',
            'category': 'cosmetiques-beaute',
            'original': 680, 'discount': 30,
            'expiry_days': 90,
            'qty': 60, 'unit': 'pot',
            'weight': 220,
            'description': 'Crème légère à l\'huile de jojoba pour visage, mains et corps. Hydratation intense 24h non grasse. Formule enrichie en vitamine E. Convient à tous types de peau. Dermatologiquement testée.',
            'img_kw': 'cream', 'img_seed': 1003,
        },
        {
            'name': 'Magné B6 — boîte 60 comprimés',
            'category': 'sante-pharmacie',
            'original': 890, 'discount': 45,
            'expiry_days': 30,
            'qty': 40, 'unit': 'boîte',
            'weight': 95,
            'description': 'Association magnésium + vitamine B6. Réduit la fatigue, les crampes musculaires et le stress. Idéal en période d\'examens ou de forte activité physique. 2 comprimés par jour avec un verre d\'eau.',
            'img_kw': 'supplement', 'img_seed': 1004,
        },
        {
            'name': 'Sirop Toplexil 150ml — toux sèche',
            'category': 'sante-pharmacie',
            'original': 550, 'discount': 50,
            'expiry_days': 20,
            'qty': 35, 'unit': 'flacon',
            'weight': 180,
            'description': 'Sirop antitussif à l\'oxomémazine. Traitement symptomatique de la toux sèche chez l\'adulte et l\'enfant de plus de 2 ans. Flacon de 150ml avec mesurette graduée.',
            'img_kw': 'syrup', 'img_seed': 1005,
        },
        {
            'name': 'Gel hydro-alcoolique 500ml — désinfectant mains',
            'category': 'hygiene-soins',
            'original': 380, 'discount': 60,
            'expiry_days': 75,
            'qty': 200, 'unit': 'flacon',
            'weight': 520,
            'description': 'Solution hydroalcoolique antibactérienne à 70% d\'alcool. Élimine 99,9% des bactéries et virus. Action rapide, sans rinçage. Formule avec aloe vera pour ne pas dessécher les mains.',
            'img_kw': 'sanitizer', 'img_seed': 1006,
        },
    ],

    'beauty_plus_oran': [
        {
            'name': 'Parfum Chanel N°5 EDP 50ml',
            'category': 'cosmetiques-beaute',
            'original': 8500, 'discount': 40,
            'expiry_days': 120,
            'qty': 12, 'unit': 'flacon',
            'weight': 180,
            'description': 'L\'iconique parfum Chanel N°5 en eau de parfum. Notes de tête : aldéhydes, néroli, ylang-ylang. Notes de cœur : rose, jasmin, iris. Notes de fond : vétiver, santal, musc. 50ml vaporisateur.',
            'img_kw': 'perfume', 'img_seed': 2001,
        },
        {
            'name': 'Fond de teint L\'Oréal Infaillible 24H — teinte 120',
            'category': 'cosmetiques-beaute',
            'original': 1200, 'discount': 35,
            'expiry_days': 60,
            'qty': 25, 'unit': 'flacon',
            'weight': 90,
            'description': 'Fond de teint longue tenue 24h résistant à l\'eau et à la transpiration. Couvrance modulable, fini naturel. SPF 25. Convient aux peaux mixtes à grasses. Teinte Vanilla 120.',
            'img_kw': 'foundation', 'img_seed': 2002,
        },
        {
            'name': 'Palette de maquillage Urban Decay Naked 3',
            'category': 'cosmetiques-beaute',
            'original': 5800, 'discount': 50,
            'expiry_days': 90,
            'qty': 8, 'unit': 'palette',
            'weight': 350,
            'description': 'Palette 12 ombres à paupières nudes roses aux finitions mates et shimmer. Pigmentation intense, longue durée. Inclus pinceau double embout. Parfaite pour look naturel ou smoky.',
            'img_kw': 'makeup', 'img_seed': 2003,
        },
        {
            'name': 'Shampoing Kérastase Nutritive 500ml',
            'category': 'cosmetiques-beaute',
            'original': 2200, 'discount': 45,
            'expiry_days': 80,
            'qty': 30, 'unit': 'flacon',
            'weight': 530,
            'description': 'Shampoing nourrissant pour cheveux secs à très secs. Formule enrichie en Irisome Complex qui nourrit en profondeur la fibre capillaire. Cheveux doux, brillants et faciles à coiffer. 500ml.',
            'img_kw': 'shampoo', 'img_seed': 2004,
        },
        {
            'name': 'Rouge à lèvres MAC Satin — Ruby Woo',
            'category': 'cosmetiques-beaute',
            'original': 1800, 'discount': 30,
            'expiry_days': 100,
            'qty': 18, 'unit': 'stick',
            'weight': 45,
            'description': 'Rouge à lèvres iconique MAC en rouge vif classique. Formule satin pour un confort optimal. Longue tenue jusqu\'à 8h. S\'applique facilement pour un résultat net et précis.',
            'img_kw': 'lipstick', 'img_seed': 2005,
        },
        {
            'name': 'Sérum anti-âge Vichy LiftActiv Supreme 30ml',
            'category': 'cosmetiques-beaute',
            'original': 3200, 'discount': 55,
            'expiry_days': 40,
            'qty': 15, 'unit': 'flacon',
            'weight': 75,
            'description': 'Sérum concentré anti-rides et anti-taches. Réduit visiblement les rides en 10 jours. Contient 15% de vitamines C, B3 et acide hyaluronique. Peau repulpée, éclat retrouvé. Testé dermatologiquement.',
            'img_kw': 'serum', 'img_seed': 2006,
        },
    ],

    'bionature_constantine': [
        {
            'name': 'Huile d\'Argan Pure 100ml — certifiée bio',
            'category': 'bio-naturel',
            'original': 1800, 'discount': 40,
            'expiry_days': 70,
            'qty': 45, 'unit': 'flacon',
            'weight': 125,
            'description': 'Huile d\'argan pure pressée à froid, certifiée biologique. Hydrate et nourrit la peau, les cheveux et les ongles. Riche en acides gras insaturés et vitamine E. Origine Maroc — certification ECOCERT.',
            'img_kw': 'oil', 'img_seed': 3001,
        },
        {
            'name': 'Tisane Minceur BIO — boîte 20 sachets',
            'category': 'bio-naturel',
            'original': 650, 'discount': 30,
            'expiry_days': 50,
            'qty': 80, 'unit': 'boîte',
            'weight': 60,
            'description': 'Mélange de plantes bio : ortie, pissenlit, fenouil, citron. Favorise l\'élimination naturelle et le drainage. Sans théine ni additifs. Idéale le soir après le repas. 20 sachets biodégradables.',
            'img_kw': 'herbal', 'img_seed': 3002,
        },
        {
            'name': 'Miel de Sidr Yéménite 500g',
            'category': 'bio-naturel',
            'original': 3500, 'discount': 25,
            'expiry_days': 180,
            'qty': 20, 'unit': 'pot',
            'weight': 600,
            'description': 'Miel de Sidr pur, récolté dans les montagnes de l\'Hadramaout. Riche en antioxydants, vitamines et minéraux. Propriétés antibactériennes naturelles. Texture épaisse et couleur ambrée foncée. Pot en verre 500g.',
            'img_kw': 'honey', 'img_seed': 3003,
        },
        {
            'name': 'Spiruline en poudre 200g — super-aliment',
            'category': 'bio-naturel',
            'original': 1200, 'discount': 35,
            'expiry_days': 55,
            'qty': 35, 'unit': 'sachet',
            'weight': 220,
            'description': 'Spiruline 100% pure, culture biologique contrôlée. Riche en protéines (60-70%), vitamines B12, fer et antioxydants. Idéale dans un smoothie ou yaourt. Sachet refermable 200g.',
            'img_kw': 'spirulina', 'img_seed': 3004,
        },
        {
            'name': 'Savon d\'Alep authentique 190g — 30% laurier',
            'category': 'bio-naturel',
            'original': 420, 'discount': 20,
            'expiry_days': 200,
            'qty': 100, 'unit': 'savon',
            'weight': 200,
            'description': 'Savon d\'Alep traditionnel artisanal, 30% huile de laurier + 70% huile d\'olive. Convient à toutes peaux, notamment peaux sensibles et atopiques. Fabriqué selon méthode ancestrale syrienne.',
            'img_kw': 'soap', 'img_seed': 3005,
        },
        {
            'name': 'Graines de chia biologiques 500g',
            'category': 'bio-naturel',
            'original': 980, 'discount': 40,
            'expiry_days': 65,
            'qty': 55, 'unit': 'sachet',
            'weight': 510,
            'description': 'Graines de chia biologiques certifiées. Riches en oméga-3, fibres et calcium. Sans gluten. À incorporer dans yaourts, smoothies ou puddings. Source d\'énergie naturelle et durable. Sachet 500g.',
            'img_kw': 'seeds', 'img_seed': 3006,
        },
    ],

    'sportzone_blida': [
        {
            'name': 'Whey Protein Gold Standard 2kg — Chocolat',
            'category': 'sport-bien-etre',
            'original': 7500, 'discount': 30,
            'expiry_days': 50,
            'qty': 18, 'unit': 'pot',
            'weight': 2100,
            'description': 'Protéine whey concentrée 100% pure de Optimum Nutrition. 24g de protéines par portion, 5,5g de BCAA naturels. Faible teneur en sucres et lipides. Mélange facilement. Saveur chocolat intense.',
            'img_kw': 'protein', 'img_seed': 4001,
        },
        {
            'name': 'Gants de musculation Nike — Taille M',
            'category': 'sport-bien-etre',
            'original': 1800, 'discount': 45,
            'expiry_days': 120,
            'qty': 22, 'unit': 'paire',
            'weight': 180,
            'description': 'Gants de musculation Nike avec rembourrage sur la paume. Velcro ajustable au poignet. Matière respirante évitant la transpiration. Taille M (tour de main 18-19cm). Mixte homme/femme.',
            'img_kw': 'gloves', 'img_seed': 4002,
        },
        {
            'name': 'Barres Énergétiques PowerBar — boîte 12×60g',
            'category': 'sport-bien-etre',
            'original': 2400, 'discount': 50,
            'expiry_days': 25,
            'qty': 30, 'unit': 'boîte',
            'weight': 800,
            'description': 'Barres énergétiques PowerBar Performance Energy, 12 barres de 60g. Saveur fruits rouges. Formule C2MAX de glucides optimisés. Idéales pendant l\'effort sportif. Sans colorants artificiels.',
            'img_kw': 'fitness', 'img_seed': 4003,
        },
        {
            'name': 'Tapis de yoga antidérapant 6mm — Bleu',
            'category': 'sport-bien-etre',
            'original': 2200, 'discount': 35,
            'expiry_days': 150,
            'qty': 14, 'unit': 'tapis',
            'weight': 1100,
            'description': 'Tapis de yoga en TPE écologique, épaisseur 6mm. Revêtement antidérapant des deux côtés. Léger et facile à transporter avec sangle. Dimensions 183×61cm. Sans latex, sans phtalates.',
            'img_kw': 'yoga', 'img_seed': 4004,
        },
        {
            'name': 'Boisson isotonique Gatorade 1L — Orange',
            'category': 'sport-bien-etre',
            'original': 380, 'discount': 40,
            'expiry_days': 15,
            'qty': 60, 'unit': 'bouteille',
            'weight': 1050,
            'description': 'Boisson isotonique Gatorade Thirst Quencher. Recharge en électrolytes (sodium, potassium) après l\'effort. Saveur orange rafraîchissante. Bouteille PET recyclable 1L. Idéale pour sports collectifs.',
            'img_kw': 'beverage', 'img_seed': 4005,
        },
        {
            'name': 'Corde à sauter professionnelle Speed Rope',
            'category': 'sport-bien-etre',
            'original': 950, 'discount': 25,
            'expiry_days': 200,
            'qty': 40, 'unit': 'unité',
            'weight': 200,
            'description': 'Corde à sauter professionnelle avec câble en acier recouvert PVC. Poignées ergonomiques anti-dérapantes. Roulements à billes ultra-fluides. Longueur ajustable jusqu\'à 3m. Pour CrossFit, boxe et cardio.',
            'img_kw': 'sport', 'img_seed': 4006,
        },
    ],

    'saveurs_setif': [
        {
            'name': 'Chocolat Lindt Excellence 70% cacao — 100g',
            'category': 'confiseries-snacks',
            'original': 520, 'discount': 35,
            'expiry_days': 30,
            'qty': 75, 'unit': 'tablette',
            'weight': 110,
            'description': 'Chocolat noir Lindt Excellence 70% cacao. Notes intenses de cacao, légèrement acidulé. Fabriqué avec des fèves de cacao sélectionnées. Sans huile de palme. Tablette 100g.',
            'img_kw': 'chocolate', 'img_seed': 5001,
        },
        {
            'name': 'Biscuits Digestive McVitie\'s 400g',
            'category': 'confiseries-snacks',
            'original': 480, 'discount': 40,
            'expiry_days': 20,
            'qty': 90, 'unit': 'paquet',
            'weight': 420,
            'description': 'Biscuits sablés au blé complet McVitie\'s. Légèrement sucrés, riches en fibres. Paquet refermable 400g. Idéaux pour le petit-déjeuner ou goûter. Source de fibres alimentaires. Saveur nature.',
            'img_kw': 'biscuits', 'img_seed': 5002,
        },
        {
            'name': 'Confiture de fraises Bonne Maman 370g',
            'category': 'alimentation-seche',
            'original': 580, 'discount': 30,
            'expiry_days': 45,
            'qty': 50, 'unit': 'pot',
            'weight': 400,
            'description': 'Confiture extra de fraises Bonne Maman. Préparée avec 50g de fruits pour 100g. Sans conservateurs ni colorants artificiels. Couvercle vichy rouge iconique. Pot 370g. Idéale sur tartines et yaourts.',
            'img_kw': 'jam', 'img_seed': 5003,
        },
        {
            'name': 'Miel d\'Acacia Langnese 500g',
            'category': 'alimentation-seche',
            'original': 1200, 'discount': 25,
            'expiry_days': 90,
            'qty': 35, 'unit': 'pot',
            'weight': 550,
            'description': 'Miel d\'acacia Langnese, liquide et cristallisation lente. Goût délicat légèrement floral. Origine Europe certifiée. Idéal pour sucrer boissons et desserts. Pot verre 500g. Qualité premium depuis 1927.',
            'img_kw': 'honey', 'img_seed': 5004,
        },
        {
            'name': 'Chips Lay\'s Paprika — sachet familial 180g',
            'category': 'confiseries-snacks',
            'original': 340, 'discount': 45,
            'expiry_days': 12,
            'qty': 120, 'unit': 'sachet',
            'weight': 185,
            'description': 'Chips Lay\'s aromatisées au paprika doux. Cuites dans de l\'huile de tournesol. Croustillantes et savoureuses. Sachet familial 180g. Parfaites pour les soirées en famille ou entre amis.',
            'img_kw': 'chips', 'img_seed': 5005,
        },
        {
            'name': 'Pâtes Barilla Spaghetti n°5 — 500g',
            'category': 'alimentation-seche',
            'original': 280, 'discount': 20,
            'expiry_days': 100,
            'qty': 150, 'unit': 'paquet',
            'weight': 510,
            'description': 'Spaghetti Barilla 100% semoule de blé dur. Cuisson 9 minutes. Tient bien la cuisson. Riche en glucides complexes et protéines végétales. Paquet 500g. La référence mondiale des pâtes italiennes.',
            'img_kw': 'pasta', 'img_seed': 5006,
        },
    ],

    'cave_tlemcen': [
        {
            'name': 'Jus d\'Orange Tropicana 1L — pur jus',
            'category': 'boissons',
            'original': 380, 'discount': 30,
            'expiry_days': 8,
            'qty': 80, 'unit': 'litre',
            'weight': 1050,
            'description': 'Pur jus d\'orange Tropicana, pressé à froid. 100% pur jus sans sucres ajoutés, sans conservateurs. Source naturelle de vitamine C. Carton 1L. Réfrigérer après ouverture et consommer sous 4 jours.',
            'img_kw': 'juice', 'img_seed': 6001,
        },
        {
            'name': 'Eau minérale Evian — pack 6×1,5L',
            'category': 'boissons',
            'original': 650, 'discount': 20,
            'expiry_days': 180,
            'qty': 40, 'unit': 'pack',
            'weight': 9500,
            'description': 'Eau minérale naturelle Evian des Alpes françaises. Minéralisation équilibrée, idéale pour toute la famille. pH neutre 7,2. Pack de 6 bouteilles PET recyclables de 1,5L. Légère en goût.',
            'img_kw': 'water', 'img_seed': 6002,
        },
        {
            'name': 'Thé Vert Lipton — boîte 100 sachets',
            'category': 'boissons',
            'original': 580, 'discount': 40,
            'expiry_days': 25,
            'qty': 65, 'unit': 'boîte',
            'weight': 180,
            'description': 'Thé vert Lipton, mélange délicat de feuilles sélectionnées. Riche en antioxydants. Infusion 2-3 minutes à 80°C. Sachets pyramidaux pour une meilleure infusion. Boîte de 100 sachets.',
            'img_kw': 'tea', 'img_seed': 6003,
        },
        {
            'name': 'Café Nescafé Classic 200g — soluble',
            'category': 'boissons',
            'original': 1100, 'discount': 35,
            'expiry_days': 35,
            'qty': 45, 'unit': 'pot',
            'weight': 215,
            'description': 'Café soluble Nescafé Classic 200g. Arôme intense et saveur équilibrée. Préparation rapide : 1 cuillère dans l\'eau chaude. Fabriqué à partir de grains de café arabica et robusta sélectionnés.',
            'img_kw': 'coffee', 'img_seed': 6004,
        },
        {
            'name': 'Soda Coca-Cola — pack 6×33cl canettes',
            'category': 'boissons',
            'original': 540, 'discount': 25,
            'expiry_days': 60,
            'qty': 100, 'unit': 'pack',
            'weight': 2100,
            'description': 'Coca-Cola Original taste en canettes 33cl. La boisson gazeuse emblématique depuis 1886. Pack économique de 6 canettes. À servir bien frais à 4°C. Contient 10,6g de sucres pour 100ml.',
            'img_kw': 'cola', 'img_seed': 6005,
        },
        {
            'name': 'Lait entier Candia 1L — UHT',
            'category': 'produits-laitiers',
            'original': 260, 'discount': 15,
            'expiry_days': 55,
            'qty': 200, 'unit': 'litre',
            'weight': 1050,
            'description': 'Lait entier UHT Candia Grand Lait. Riche en calcium et protéines. Conservation longue durée sans réfrigération avant ouverture. Source de vitamines D et B2. Briquette 1L.',
            'img_kw': 'milk', 'img_seed': 6006,
        },
    ],

    'bebe_confort_annaba': [
        {
            'name': 'Couches Pampers Active Baby taille 3 — 64 pièces',
            'category': 'hygiene-soins',
            'original': 2200, 'discount': 30,
            'expiry_days': 70,
            'qty': 25, 'unit': 'paquet',
            'weight': 2100,
            'description': 'Couches Pampers Active Baby taille 3 (6-10 kg). Absorption triple avec cœur absorbant 3 couches. Indicateur d\'humidité, élastiques en forme de X. Jusqu\'à 12h de protection contre les fuites.',
            'img_kw': 'diapers', 'img_seed': 7001,
        },
        {
            'name': 'Lait maternisé Aptamil 1er âge — 800g',
            'category': 'sante-pharmacie',
            'original': 3800, 'discount': 20,
            'expiry_days': 40,
            'qty': 15, 'unit': 'boîte',
            'weight': 870,
            'description': 'Lait infantile Aptamil 1er âge (0-6 mois). Formule avec prébiotiques GOS/FOS. Enrichi en DHA, ARA et vitamine D. Préparation : 1 mesure pour 30ml d\'eau à 40°C. Boîte métal 800g.',
            'img_kw': 'formula', 'img_seed': 7002,
        },
        {
            'name': 'Lingettes bébé Huggies Pure — pack 3×64 pièces',
            'category': 'hygiene-soins',
            'original': 980, 'discount': 35,
            'expiry_days': 80,
            'qty': 50, 'unit': 'pack',
            'weight': 750,
            'description': 'Lingettes bébé Huggies Pure aux 99% d\'eau pure. Sans parfum, sans alcool, sans parabènes. Douces pour la peau sensible des bébés. Testées dermatologiquement. Pack économique 3×64 lingettes.',
            'img_kw': 'baby', 'img_seed': 7003,
        },
        {
            'name': 'Thermomètre digital rectal Braun — ThermoScan',
            'category': 'sante-pharmacie',
            'original': 2800, 'discount': 40,
            'expiry_days': 300,
            'qty': 10, 'unit': 'unité',
            'weight': 95,
            'description': 'Thermomètre auriculaire Braun ThermoScan 5. Mesure en 1 seconde. Embout pré-chauffé pour une mesure précise. Mémoire de la dernière mesure. Inclus 21 embouts jetables. Écran couleur.',
            'img_kw': 'thermometer', 'img_seed': 7004,
        },
        {
            'name': 'Crème soin bébé Mustela Hydra Bébé 150ml',
            'category': 'cosmetiques-beaute',
            'original': 1600, 'discount': 45,
            'expiry_days': 55,
            'qty': 20, 'unit': 'tube',
            'weight': 170,
            'description': 'Crème hydratante visage pour bébé Mustela. Formule douce hypoallergénique avec extrait de tournesol. Hydratation 24h, texture fondante non grasse. Dès la naissance. Testée sous contrôle pédiatrique.',
            'img_kw': 'skincare', 'img_seed': 7005,
        },
        {
            'name': 'Doudou lapin Jellycat Bashful 30cm',
            'category': 'hygiene-soins',
            'original': 2400, 'discount': 25,
            'expiry_days': 365,
            'qty': 8, 'unit': 'unité',
            'weight': 180,
            'description': 'Doudou lapin Jellycat Bashful en peluche ultra-douce. Taille medium 30cm. Lavable en machine à 30°C. Certifié CE, sans danger dès la naissance. Matière: 100% polyester doux. Couleur beige.',
            'img_kw': 'plush', 'img_seed': 7006,
        },
    ],

    'hygiene_pro_bejaia': [
        {
            'name': 'Détergent lave-vaisselle Finish Ultimate — 60 pastilles',
            'category': 'hygiene-soins',
            'original': 1400, 'discount': 40,
            'expiry_days': 50,
            'qty': 35, 'unit': 'boîte',
            'weight': 980,
            'description': 'Pastilles lave-vaisselle Finish Ultimate tout-en-un. Dissolvent les taches tenaces, dégraissent, rincent et font briller. Action en eau froide. Sans phosphates. Boîte de 60 pastilles.',
            'img_kw': 'dishwasher', 'img_seed': 8001,
        },
        {
            'name': 'Lessive liquide Ariel 3L — 40 lavages',
            'category': 'hygiene-soins',
            'original': 1800, 'discount': 35,
            'expiry_days': 90,
            'qty': 28, 'unit': 'bidon',
            'weight': 3200,
            'description': 'Lessive liquide Ariel Original 3L. Formule concentrée pour 40 lavages à 30°C. Élimine les taches dès le premier lavage. Convient aux vêtements blancs et de couleurs. Avec bouchon doseur intégré.',
            'img_kw': 'laundry', 'img_seed': 8002,
        },
        {
            'name': 'Nettoyant multi-surfaces Antikal 750ml',
            'category': 'hygiene-soins',
            'original': 580, 'discount': 50,
            'expiry_days': 30,
            'qty': 60, 'unit': 'flacon',
            'weight': 790,
            'description': 'Nettoyant anti-calcaire Antikal pour salle de bain et cuisine. Élimine calcaire, savon résiduel et rouille. Action rapide sans frottement excessif. Flacon spray 750ml. Parfum frais.',
            'img_kw': 'cleaning', 'img_seed': 8003,
        },
        {
            'name': 'Désinfectant Lysol surfaces 500ml',
            'category': 'hygiene-soins',
            'original': 750, 'discount': 45,
            'expiry_days': 60,
            'qty': 45, 'unit': 'flacon',
            'weight': 520,
            'description': 'Spray désinfectant Lysol à action rapide. Élimine 99,9% des bactéries, virus et champignons. Certifié virucide. Parfum lavande antibactérien. Idéal pour sanitaires, plans de travail, poignées de portes.',
            'img_kw': 'disinfectant', 'img_seed': 8004,
        },
        {
            'name': 'Papier toilette Lotus Comfort 48 rouleaux',
            'category': 'hygiene-soins',
            'original': 1600, 'discount': 20,
            'expiry_days': 200,
            'qty': 20, 'unit': 'paquet',
            'weight': 4200,
            'description': 'Papier toilette Lotus Comfort 3 épaisseurs. Extra doux et résistant. 48 rouleaux de 200 feuilles. Certifié FSC, issu de forêts gérées durablement. Format maxi économique.',
            'img_kw': 'tissue', 'img_seed': 8005,
        },
        {
            'name': 'Éponges Scotch-Brite triple usage — lot de 6',
            'category': 'hygiene-soins',
            'original': 380, 'discount': 30,
            'expiry_days': 300,
            'qty': 80, 'unit': 'lot',
            'weight': 160,
            'description': 'Éponges Scotch-Brite 3M combinées microfibre + grattoir. Côté doux pour surfaces délicates, côté grattant pour résidus tenaces. Lot de 6 éponges. Résistantes et longue durée d\'utilisation.',
            'img_kw': 'sponge', 'img_seed': 8006,
        },
    ],
}


class Command(BaseCommand):
    help = 'Seed FORSA database with 8 stores and 48 products with real images.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing seeded data first')
        parser.add_argument('--no-images', action='store_true', help='Skip image downloads (faster)')

    def handle(self, *args, **options):
        download = not options['no_images']

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing seeded users/stores/products...'))
            for sd in STORES_DATA:
                User.objects.filter(username=sd['username']).delete()
            self.stdout.write(self.style.SUCCESS('Cleared.\n'))

        # ── 1. Ensure categories exist ────────────────────────
        self.stdout.write('[*] Checking categories...')
        from django.core.management import call_command
        call_command('seed_categories', verbosity=0)

        # ── 2. Create stores + users ─────────────────────────
        self.stdout.write('\n[*] Creating stores...')
        for sd in STORES_DATA:
            user, created = User.objects.get_or_create(
                username=sd['username'],
                defaults={
                    'email':      sd['email'],
                    'first_name': sd['first_name'],
                    'last_name':  sd['last_name'],
                    'role':       'vendor',
                    'wilaya':     sd['wilaya'],
                    'phone':      sd['phone'],
                    'is_verified': True,
                }
            )
            if created:
                user.set_password(sd['password'])
                user.save()

            city_name, lat, lng = CITIES[sd['wilaya']]

            store, s_created = Store.objects.get_or_create(
                owner=user,
                defaults={
                    'name':        sd['name'],
                    'description': sd['description'],
                    'phone':       sd['phone'],
                    'wilaya':      sd['wilaya'],
                    'address':     sd['address'],
                    'rating':      sd['rating'],
                    'latitude':    lat,
                    'longitude':   lng,
                    'status':      'active',
                    'total_sales': 0,
                }
            )

            if download:
                needs_save = False
                if not store.logo:
                    logo_data = download_image(loremflickr(sd['logo_kw'], sd['logo_seed'], 200, 200))
                    if logo_data is not None:
                        store.logo.save(f"logo_{sd['logo_seed']}.jpg", logo_data, save=False)
                        needs_save = True
                if not store.banner:
                    banner_data = download_image(loremflickr(sd['banner_kw'], sd['banner_seed'], 800, 300))
                    if banner_data is not None:
                        store.banner.save(f"banner_{sd['banner_seed']}.jpg", banner_data, save=False)
                        needs_save = True
                if needs_save:
                    store.save()

            status = '[+] Cree' if s_created else '[=] Existe'
            self.stdout.write(f"   {status} : {sd['name']} ({city_name})")

        # ── 3. Create products ────────────────────────────────
        self.stdout.write('\n[*] Creating products...')
        today = date.today()
        total_products = 0
        total_images   = 0

        for username, products in PRODUCTS_DATA.items():
            try:
                store = Store.objects.get(owner__username=username)
            except Store.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'   [!] Store not found for {username}'))
                continue

            for pd in products:
                try:
                    cat = Category.objects.get(slug=pd['category'])
                except Category.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'   [!] Category {pd["category"]} not found, skipping.'))
                    continue

                orig    = Decimal(str(pd['original']))
                disc    = Decimal(str(pd['discount']))
                current = (orig * (100 - disc) / 100).quantize(Decimal('1'))
                expiry  = today + timedelta(days=pd['expiry_days'])

                product, p_created = Product.objects.get_or_create(
                    store=store,
                    name=pd['name'],
                    defaults={
                        'category':       cat,
                        'description':    pd['description'],
                        'original_price': orig,
                        'current_price':  current,
                        'discount_pct':   disc,
                        'expiry_date':    expiry,
                        'quantity':       pd['qty'],
                        'unit':           pd['unit'],
                        'weight_grams':   pd.get('weight'),
                        'status':         'active',
                        'is_featured':    pd.get('expiry_days', 999) <= 60,
                        'views_count':    0,
                        'sales_count':    0,
                    }
                )

                if p_created:
                    total_products += 1
                    self.stdout.write(f"   [+] {store.name[:20]:20} -> {pd['name'][:45]}")

                if download and not product.images.exists():
                    self.stdout.write(f"   [img] Downloading images for: {pd['name'][:40]}")
                    img_data = download_image(loremflickr(pd['img_kw'], pd['img_seed']))
                    if img_data is not None:
                        pi = ProductImage(product=product, is_primary=True, order=0)
                        pi.image.save(f"prod_{pd['img_seed']}.jpg", img_data, save=True)
                        total_images += 1
                    img_data2 = download_image(loremflickr(pd['img_kw'], pd['img_seed'] + 500))
                    if img_data2 is not None:
                        pi2 = ProductImage(product=product, is_primary=False, order=1)
                        pi2.image.save(f"prod_{pd['img_seed']}_b.jpg", img_data2, save=True)
                        total_images += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n[OK] Done! Created {total_products} products and downloaded {total_images} images.\n'
            f'     Run `python manage.py runserver` and visit http://127.0.0.1:8000/'
        ))
