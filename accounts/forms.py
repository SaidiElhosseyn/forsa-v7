from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, WILAYA_CHOICES

FC   = 'form-control'   # CSS class applied by FORSA CSS
FCWI = {'class': FC}    # standard input
FCWT = {'class': FC, 'rows': 3}  # textarea

WILAYA_CHOICES_WITH_EMPTY = [('', '— Sélectionner votre wilaya —')] + list(WILAYA_CHOICES)


# ──────────────────────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────────────────────
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={
            **FCWI,
            'placeholder': 'Votre nom d\'utilisateur',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            **FCWI,
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
            'id': 'id_password',
        })
    )
    error_messages = {
        'invalid_login': "Nom d'utilisateur ou mot de passe incorrect. Vérifiez vos identifiants.",
        'inactive': "Ce compte est désactivé.",
    }


# ──────────────────────────────────────────────────────────
# REGISTER — CUSTOMER
# ──────────────────────────────────────────────────────────
class CustomerRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label='Prénom',
        widget=forms.TextInput(attrs={**FCWI, 'placeholder': 'Votre prénom'})
    )
    last_name = forms.CharField(
        label='Nom',
        widget=forms.TextInput(attrs={**FCWI, 'placeholder': 'Votre nom de famille'})
    )
    email = forms.EmailField(
        label='Adresse email',
        widget=forms.EmailInput(attrs={**FCWI, 'placeholder': 'email@exemple.com', 'autocomplete': 'email'})
    )
    phone = forms.CharField(
        label='Téléphone',
        widget=forms.TextInput(attrs={**FCWI, 'placeholder': '0550 000 000'})
    )
    wilaya = forms.ChoiceField(
        label='Wilaya',
        choices=WILAYA_CHOICES_WITH_EMPTY,
        widget=forms.Select(attrs={**FCWI})
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={**FCWI, 'placeholder': 'Minimum 8 caractères', 'id': 'id_password1'})
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={**FCWI, 'placeholder': 'Répétez le mot de passe', 'id': 'id_password2'})
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'wilaya', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={**FCWI, 'placeholder': 'Choisissez un identifiant unique', 'autocomplete': 'username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_wilaya(self):
        w = self.cleaned_data.get('wilaya')
        if not w:
            raise forms.ValidationError("Veuillez sélectionner votre wilaya.")
        return w

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.wilaya = self.cleaned_data['wilaya']
        if commit:
            user.save()
            # Auto-create virtual card
            try:
                from .models import VirtualCard
                VirtualCard.objects.create(user=user)
            except Exception:
                pass
        return user


# ──────────────────────────────────────────────────────────
# REGISTER — VENDOR
# ──────────────────────────────────────────────────────────
class VendorRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label='Prénom',
        widget=forms.TextInput(attrs={**FCWI, 'placeholder': 'Votre prénom'})
    )
    last_name = forms.CharField(
        label='Nom',
        widget=forms.TextInput(attrs={**FCWI, 'placeholder': 'Votre nom de famille'})
    )
    email = forms.EmailField(
        label='Email professionnel',
        widget=forms.EmailInput(attrs={**FCWI, 'placeholder': 'email@entreprise.com'})
    )
    phone = forms.CharField(
        label='Téléphone',
        widget=forms.TextInput(attrs={**FCWI, 'placeholder': '0550 000 000'})
    )
    wilaya = forms.ChoiceField(
        label='Wilaya',
        choices=WILAYA_CHOICES_WITH_EMPTY,
        widget=forms.Select(attrs={**FCWI})
    )
    address = forms.CharField(
        label='Adresse complète',
        required=False,
        widget=forms.Textarea(attrs={**FCWT, 'placeholder': 'N° rue, quartier, commune...'})
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={**FCWI, 'placeholder': 'Minimum 8 caractères', 'id': 'id_password1'})
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={**FCWI, 'placeholder': 'Répétez le mot de passe', 'id': 'id_password2'})
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'wilaya', 'address', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={**FCWI, 'placeholder': 'Identifiant unique pour votre boutique'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_wilaya(self):
        w = self.cleaned_data.get('wilaya')
        if not w:
            raise forms.ValidationError("Veuillez sélectionner votre wilaya.")
        return w

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role    = 'vendor'
        user.email   = self.cleaned_data['email']
        user.phone   = self.cleaned_data['phone']
        user.wilaya  = self.cleaned_data['wilaya']
        user.address = self.cleaned_data.get('address', '')
        if commit:
            user.save()
        return user


# ──────────────────────────────────────────────────────────
# PROFILE UPDATE
# ──────────────────────────────────────────────────────────
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'wilaya', 'address', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs=FCWI),
            'last_name':  forms.TextInput(attrs=FCWI),
            'email':      forms.EmailInput(attrs=FCWI),
            'phone':      forms.TextInput(attrs={**FCWI, 'placeholder': '0550 000 000'}),
            'wilaya':     forms.Select(attrs=FCWI, choices=WILAYA_CHOICES_WITH_EMPTY),
            'address':    forms.Textarea(attrs={**FCWT, 'placeholder': 'Votre adresse complète'}),
            'avatar':     forms.FileInput(attrs={'class': FC, 'accept': 'image/*'}),
        }


# ──────────────────────────────────────────────────────────
# PASSWORD CHANGE (custom styled)
# ──────────────────────────────────────────────────────────
class StyledPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='Mot de passe actuel',
        widget=forms.PasswordInput(attrs={**FCWI, 'placeholder': '••••••••', 'autocomplete': 'current-password'})
    )
    new_password1 = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput(attrs={**FCWI, 'placeholder': 'Minimum 8 caractères', 'autocomplete': 'new-password'})
    )
    new_password2 = forms.CharField(
        label='Confirmer le nouveau mot de passe',
        widget=forms.PasswordInput(attrs={**FCWI, 'placeholder': 'Répétez le nouveau mot de passe', 'autocomplete': 'new-password'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_pw = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_pw):
            raise forms.ValidationError("Mot de passe actuel incorrect.")
        return old_pw

    def clean(self):
        cd = super().clean()
        p1 = cd.get('new_password1')
        p2 = cd.get('new_password2')
        if p1 and p2 and p1 != p2:
            self.add_error('new_password2', 'Les deux mots de passe ne correspondent pas.')
        if p1 and len(p1) < 8:
            self.add_error('new_password1', 'Le mot de passe doit contenir au moins 8 caractères.')
        return cd

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user
