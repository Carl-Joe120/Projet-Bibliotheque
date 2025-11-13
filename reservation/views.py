from django.shortcuts import render , get_object_or_404 , redirect
from django.http import HttpRequest , HttpResponse
from livres.models import Livre , Categorie
from .models import Reservation
from utilisateurs.models import Utilisateur
from datetime import date
from django.db.models import Count , Q 
from django.contrib.auth.decorators import login_required 
from .forms import ReservationForms
from django.contrib import messages
from django.template.loader import render_to_string
import pdfkit
# Create your views here.
'''
fòm pou rezève liv, lis rezèvasyon itilizatè

'''

@login_required
def afficher_page_reservation(request):    
    categories = Categorie.objects.annotate(nb_livres=Count('livre')).filter(nb_livres__gt=0)
    livres_par_categorie = {}
    
    
    livre = Livre.objects.all()
    
    
    from .forms  import ReservationForms
    form = ReservationForms()
    for cat in categories:
        livres = Livre.objects.filter(categorie=cat, disponible=True)
        
        if livres.exists():
            livres_par_categorie[cat.nom] = livres
            
            
    context = {
        'livres_par_categorie': livres_par_categorie,        
        'search_scope': livre,
        'form': form,
       
        
    }
            
    return render(request , 'reservation/form_reservation.html' , context)


@login_required
def trouver_auteur_ou_titre(request):
    query = request.GET.get('q', '').strip()
    livres = Livre.objects.all()

    # ajoute form pou modal la ka rande jaden yo menm apre rechèch
    from .forms import ReservationForms
    form = ReservationForms()
    
    aucun_resultat = False

    if query:
        livres_auteur = livres.filter(Q(auteur__icontains=query) | Q(titre__icontains=query))
        if livres_auteur.exists():            
            livres_par_categorie = {"Résultats": livres_auteur} 
            aucun_resultat = False
        else:
            livres_par_categorie = {}
            aucun_resultat = True    
    else:
        # si rechèch la vid, retounen lis kategori / liv disponib tankou nan paj prensipal la
        categories = Categorie.objects.annotate(nb_livres=Count('livre')).filter(nb_livres__gt=0)
        livres_par_categorie = {}
        for cat in categories:
            livres_cat = Livre.objects.filter(categorie=cat, disponible=True)
            if livres_cat.exists():
                livres_par_categorie[cat.nom] = livres_cat
        aucun_resultat = False

    context = {
        'livres_par_categorie': livres_par_categorie,
        'search_scope': livres,
        'query': query,
        'form': form,
        'aucun_resultat': aucun_resultat,
    }

    return render(request, 'reservation/form_reservation.html', context)

    
@login_required
def reserver_livre(request, id):
    livre = get_object_or_404(Livre, id=id)
    print(" Requête reçue :", request.method)
    
    if request.method == 'POST':
        form = ReservationForms(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.utilisateur = request.user
            reservation.livre = livre
            reservation.livre_demande = livre.titre
            reservation.type_reservation = "physique"
            reservation.save()
            
            print("Réservation enregistrée :" , reservation.id)
            messages.success(request, "Réservation effectuée avec succès ")
            return redirect('mes_reservations')
        else:
            print(" Erreur form:", form.errors)
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = ReservationForms()

    return render(request, 'reservation/soumission_reservation.html', {
        'livre': livre,
        'form': form
    })

       

@login_required
def detail_reservation(request , id):
    reservation = get_object_or_404(Reservation , id = id)
    
    if reservation.utilisateur != request.user:
        HttpResponse("Accès non autorisé" , status = 403)
    
    context = {
        'reservation' : reservation
    }
    
    return render(request , 'reservation/detail_reservation.html' , context)

@login_required 
def telecharger_recu(request , id):
    telechargement = get_object_or_404(Reservation , id = id)
    context = {
        'telechargement' : telechargement
    }
    
    html = render_to_string('reservation/recu_template.html' , context)
    
    pdf = pdfkit.from_string(html , False)
    reponse = HttpResponse(pdf , content_type = 'application/pdf')
    reponse['Content-Disposition'] = f'attachement; filename="recu_reservation_{id}.pdf"'
    
    
@login_required
def mes_reservations(request):
    reservations = Reservation.objects.filter(utilisateur = request.user)
    context = {
        'reservations' : reservations
    }
    
    return render(request , 'reservation/mes_reservations.html' , context)