from django import forms
from django.utils import timezone
from .models import Product, Category

FC = {'class': 'form-control'}


class ProductForm(forms.ModelForm):
    """
    Formulaire produit vendeur.
    Le vendeur saisit le prix original + sa réduction manuelle (%).
    current_price est calculé automatiquement.
    """
    discount_pct = forms.DecimalField(
        label='Réduction manuelle (%)',
        min_value=0,
        max_value=90,
        decimal_places=0,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={
            **FC,
            'step': '1',
            'min': '0',
            'max': '90',
            'placeholder': 'Ex : 20  →  prix affiché = prix × 0.80',
        }),
        help_text='Entre 0 et 90 %. Si 0, prix réduit = prix original. '
                  'La réduction automatique FORSA s\'appliquera EN PLUS selon la date.',
    )

    class Meta:
        model  = Product
        fields = [
            'category', 'name', 'description',
            'original_price', 'discount_pct',
            'expiry_date', 'quantity', 'unit',
            'weight_grams', 'barcode',
        ]
        widgets = {
            'category':       forms.Select(attrs=FC),
            'name':           forms.TextInput(attrs={**FC, 'placeholder': 'Nom du produit'}),
            'description':    forms.Textarea(attrs={**FC, 'rows': 3,
                                                    'placeholder': 'Description, composition, état...'}),
            'original_price': forms.NumberInput(attrs={**FC, 'step': '1',
                                                       'min': '1', 'placeholder': '0'}),
            'expiry_date':    forms.DateInput(attrs={**FC, 'type': 'date'}, format='%Y-%m-%d'),
            'quantity':       forms.NumberInput(attrs={**FC, 'min': '1', 'placeholder': '0'}),
            'unit':           forms.TextInput(attrs={**FC,
                                                     'placeholder': 'ex: pièce, kg, litre, boîte'}),
            'weight_grams':   forms.NumberInput(attrs={**FC, 'min': '0',
                                                       'placeholder': 'Poids en grammes (optionnel)'}),
            'barcode':        forms.TextInput(attrs={**FC,
                                                     'placeholder': 'Code-barres (optionnel)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True).order_by('order')
        self.fields['description'].required  = False
        self.fields['weight_grams'].required = False
        self.fields['barcode'].required      = False
        self.fields['discount_pct'].required = False
        # Si édition, afficher la valeur existante
        if self.instance and self.instance.pk:
            self.fields['discount_pct'].initial = int(self.instance.discount_pct or 0)

    def clean_expiry_date(self):
        d = self.cleaned_data.get('expiry_date')
        if d and d < timezone.now().date():
            raise forms.ValidationError("La date de péremption ne peut pas être dans le passé.")
        return d

    def clean_original_price(self):
        p = self.cleaned_data.get('original_price')
        if p is not None and p <= 0:
            raise forms.ValidationError("Le prix doit être supérieur à 0.")
        return p

    def clean_discount_pct(self):
        pct = self.cleaned_data.get('discount_pct') or 0
        if pct < 0 or pct > 90:
            raise forms.ValidationError("La réduction doit être entre 0% et 90%.")
        return pct
