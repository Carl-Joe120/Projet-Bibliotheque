from django import forms
from .models import Reservation

class ReservationForms(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['message_utilisateur']

        widgets = {
           
            'message_utilisateur': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Laisser un message facultatif...',
                'style': 'border-radius:10px; resize:none;',
            }),
        }
