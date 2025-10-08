from django.contrib import admin
from employes.models import Employe

# Register your models here.
from employes.models import Employe

@admin.register(Employe)
class AdminEmploye(admin.ModelAdmin):
    list_display = ('ROLE_CHOICES', 'nom_complet' , 'role' , 'date_embauche' , 'salaire_mensuel', 'actif')
    list_filter = ['role']
    search_fields = ['nom_complet']
    
    