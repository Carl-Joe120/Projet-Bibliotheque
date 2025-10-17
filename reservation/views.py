from django.shortcuts import render
from django.http import HttpRequest , HttpResponse
from livres.models import Livre , Categorie
from reservation.models import Reservation
from utilisateurs.models import Utilisateur
from datetime import date
from django.db.models import Count
# Create your views here.
'''
fòm pou rezève liv, lis rezèvasyon itilizatè

'''


def reserver_livre(request):    
    categories = Categorie.objects.annotate(nb_livres=Count('livre')).filter(nb_livres__gt=0)
    livres_par_categorie = {}
    
    
    livre = Livre.objects.all()
    
    
      
    for cat in categories:
        livres = Livre.objects.filter(categorie=cat, disponible=True)
        
        if livres.exists():
            livres_par_categorie[cat.nom] = livres
            
            
    context = {
        'livres_par_categorie': livres_par_categorie,        
        'search_scope': livre,
       
        
    }
            
    return render(request , 'reservation/form_reservation.html' , context)


def trouver_auteur_ou_titre(request):
    query = request.GET.get('q')
    livres = Livre.objects.all()
    
    if query:
        livres_auteur = livres.filter(auteur__icontains=query) | livres.filter(titre__icontains = query)
        context = livres_auteur
    return render(request , 'reservation/form_reservation.html' , context)