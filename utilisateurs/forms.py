from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from utilisateurs.models import Role, Utilisateur


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = Utilisateur
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'role', 'telephone', 'adresse', 'photo_profil',
            'is_active', 'is_staff', 'is_superuser'
        )


class SigninForm(AuthenticationForm):
    username = forms.CharField(
        max_length=20,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur"
        })
    )

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': "Mot de passe"
        })
    )

    error_messages = {
        'invalid_login': "Nom d'utilisateur ou mot de passe incorrect."
    }


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'role', 'telephone', 'adresse', 'date_de_naissance',
            'photo_profil', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class SignupForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'telephone', 'adresse', 'photo_profil',
            'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # ← Placeholder klè pou chak champ
        self.fields['username'].widget.attrs['placeholder'] = "ex: Jvc2002"
        self.fields['first_name'].widget.attrs['placeholder'] = "ex: Jean Vanel"
        self.fields['last_name'].widget.attrs['placeholder'] = "ex: Casseus"
        self.fields['email'].widget.attrs['placeholder'] = "ex: jean@gmail.com"
        self.fields['telephone'].widget.attrs['placeholder'] = "ex: 48831787"
        self.fields['adresse'].widget.attrs['placeholder'] = "ex: Delmas 75"
        self.fields['password1'].widget.attrs['placeholder'] = "Min. 8 caractères"
        self.fields['password2'].widget.attrs['placeholder'] = "Répétez le mot de passe"

        # ← Retire help_text ki twò teknik
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Utilisateur.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Ce nom d'utilisateur est déjà pris. Essayez un autre."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Un compte existe déjà avec cette adresse email. Connectez-vous plutôt."
            )
        return email


class SecretaireCreationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'telephone', 'adresse', 'date_de_naissance',
            'photo_profil', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
            
            
class VerificationCodeForm(forms.Form): code = forms.CharField( max_length=6, label="Code de vérification", widget=forms.TextInput(attrs={ 'class': 'form-control', 'placeholder': 'Entrez le code reçu par email' }) )