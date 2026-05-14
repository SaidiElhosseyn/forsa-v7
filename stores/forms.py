from django import forms
from .models import Store
from accounts.models import WILAYA_CHOICES

FC = {'class': 'form-control'}


class StoreForm(forms.ModelForm):
    class Meta:
        model  = Store
        fields = ['name', 'description', 'logo', 'banner',
                  'phone', 'wilaya', 'address', 'latitude', 'longitude']
        widgets = {
            'name':        forms.TextInput(attrs={**FC, 'placeholder': 'Nom de votre boutique'}),
            'description': forms.Textarea(attrs={**FC, 'rows': 3}),
            'logo':        forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'banner':      forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'phone':       forms.TextInput(attrs={**FC, 'placeholder': '0550 000 000'}),
            'wilaya':      forms.Select(attrs=FC,
                                        choices=[('', '— Wilaya —')] + list(WILAYA_CHOICES)),
            'address':     forms.Textarea(attrs={**FC, 'rows': 2}),
            'latitude':    forms.NumberInput(attrs={**FC, 'step': '0.000001',
                                                    'placeholder': 'ex : 36.751906'}),
            'longitude':   forms.NumberInput(attrs={**FC, 'step': '0.000001',
                                                    'placeholder': 'ex : 3.042048'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['logo'].required = False
        self.fields['banner'].required = False
        self.fields['address'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['latitude'].label  = 'Latitude GPS (optionnel)'
        self.fields['longitude'].label = 'Longitude GPS (optionnel)'
