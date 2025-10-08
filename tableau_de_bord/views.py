from django.shortcuts import render
from django.shortcuts import HttpResponse


# Create your views here.

def livres_les_plus_populaires(request):
    return render(request , 'tableau_de_bord/livres_populaires.html')


def nombre_emprunt_par_mois(request):
    return render(request , 'tableau_de_bord/nombre_emprunt_par_mois.html')


def retard_par_utilisateur(request):
    return render(request , 'tableau_de_bord/retard_par_utilisateur.html')


'''
montre dashboard ak grafik

'''