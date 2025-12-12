from django.contrib import admin
from livres.models import *

# Register your models here.

@admin.register(Categorie)
class AdminCategorie(admin.ModelAdmin):
    list_display = ('nom',)



@admin.register(Livre)
class AdminLivre(admin.ModelAdmin):
    list_display = ('titre','auteur','isbn','date_publication','categorie','couverture')
    list_filter = ['auteur']
    search_fields = ['titre' , 'categorie']
    list_per_page = 5

@admin.register(Emprunt)
class AdminEmprunt(admin.ModelAdmin):
    list_display = ('utilisateur','date_emprunt','date_retour_prevu','date_retour_effectif')
    list_filter = ['utilisateur']
    search_fields = ['date_retour_prevu']

@admin.register(Penalite)
class AdminPenalite(admin.ModelAdmin):
    list_display = ('emprunt', 'montant','paye')
    search_fields = ['paye']
    
