from .models import Livre
from django import forms
import re

class LivreForm(forms.ModelForm):

    class Meta:
        model = Livre
        fields = [
            'titre',
            'auteur',
            'isbn',
            'resume',
            'date_publication',
            'categorie',
            'quantite',
            'couverture',
            
        ]

        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'auteur': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'resume': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'date_publication': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
        }

    # validation titre
    def clean_titre(self):
        titre = self.cleaned_data.get("titre")

        if any(char.isdigit() for char in titre):
            raise forms.ValidationError(
                "Le titre ne doit pas contenir de chiffres."
            )

        return titre

    # validation auteur
    def clean_auteur(self):
        auteur = self.cleaned_data.get("auteur")

        if any(char.isdigit() for char in auteur):
            raise forms.ValidationError(
                "Le nom de l'auteur ne doit pas contenir de chiffres."
            )

        return auteur

    # validation ISBN
    def clean_isbn(self):
        isbn = self.cleaned_data.get("isbn")

        if not re.match(r'^[0-9\-]+$', isbn):
            raise forms.ValidationError(
                "ISBN doit contenir uniquement des chiffres et tirets."
            )

        return isbn

    # validation quantité
    def clean_quantite(self):
        quantite = self.cleaned_data.get("quantite")

        if quantite <= 0:
            raise forms.ValidationError(
                "La quantité doit être supérieure à 0."
            )

        return quantite