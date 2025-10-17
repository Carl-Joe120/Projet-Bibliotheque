from django.urls import path
from . import views

urlpatterns = [
    path('importer_livre_français/', views.importer_livre_français, name='importer-liv-francais'),
    path('liste_livres/', views.liste_livres, name='list_livres'),
    path('livre_empruntes/' , views.livre_empruntes , name = 'livre_empruntes')
]

