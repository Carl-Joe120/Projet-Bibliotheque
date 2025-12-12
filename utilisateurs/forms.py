from django import forms
from django.contrib.auth.forms import AuthenticationForm , UserCreationForm , UserChangeForm
from utilisateurs.models import Role , Utilisateur


class CustomUserChangeForm(UserChangeForm):
     class Meta:       
        model = Utilisateur
        fields = ('username' , 'email' , 'first_name' , 'last_name', 'role' , 'telephone' , 'adresse' , 'photo_profil' , 'is_active' , 'is_staff' , 'is_superuser')       
        
        




class SigninForm(AuthenticationForm):
    username = forms.CharField(max_length=20 , label= 'Nom d\'Utilisateur')    
    password = forms.CharField(label = "Mot de Passe" , widget = forms.PasswordInput)
    
    error_message = {
        'invalid_login': "Nom d'utilisateur ou mot de passe incorrecte"
    }



class SignupForm(UserCreationForm):
    class Meta():
        model = Utilisateur
        fields = ['username' , 'first_name' , 'last_name' , 'email' ,  'password1' , 'password2' , 'telephone' , 'adresse' , 'photo_profil']

        
