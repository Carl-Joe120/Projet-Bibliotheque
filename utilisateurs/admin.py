from django.contrib import admin
from utilisateurs.models import Utilisateur
from .models import Utilisateur
from .forms import CustomUserChangeForm , SignupForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class UtilisateurAdmin(UserAdmin):
    add_form = SignupForm
    form = CustomUserChangeForm
    model = Utilisateur
    list_display = ('username' , 'email' , 'role' , 'is_staff' , 'is_active')
    list_filter = ('role' , 'is_staff' , 'is_active')
    fieldsets = (
        (None , {'fields':('username' , 'email' , 'password')}),
        ('Informations personnelles', {'fields':('first_name', 'last_name' , 'role' , 'telephone', 'adresse' , 'photo_profil' , 'numero_membre')}),
        ('Permissions', {'fields': ('is_staff' , 'is_active' , 'is_superuser')}),
    
    )
    
    add_fieldsets = (
        (None , {
            'classes':('wide',),
            'fields': ('username' , 'email' , 'first_name' , 'last_name' , 'role' , 'telephone' , 'adresse', 'photo_profil' , 'password1' , 'password2' , 'is_staff' , 'is_active')
            
        }),
        
    )
    
    search_fields = ('email' , 'username') 
    ordering = ('username' , )
    



admin.site.register(Utilisateur , UtilisateurAdmin)