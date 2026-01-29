from django.shortcuts import render , get_object_or_404 , redirect
from django.http import HttpRequest , HttpResponse , JsonResponse
from livres.models import Livre , Categorie , Emprunt
from .models import Reservation , ReservationStatus
from utilisateurs.models import Utilisateur
from datetime import date
from django.db.models import Count , Q 
from django.contrib.auth.decorators import login_required 
from .forms import ReservationForms
from django.contrib import messages
from django.template.loader import render_to_string
import pdfkit
from django.db import transaction
from .utils import generer_pdf_qr

# Create your views here.
'''
fòm pou rezève liv, lis rezèvasyon itilizatè

'''

@login_required
def afficher_page_reservation(request):    
    categories = Categorie.objects.annotate(nb_livres=Count('livre')).filter(nb_livres__gt=0)
    livres_par_categorie = {}
    
    from .forms  import ReservationForms
    form = ReservationForms()
    
    for cat in categories:
        livres = Livre.objects.filter(categorie=cat)
        
        livres_disponibles = [liv for liv in livres if livre_disponible(liv)]
        
        if livres_disponibles:
            livres_par_categorie[cat.nom] = livres_disponibles
            
            
    context = {
        'livres_par_categorie': livres_par_categorie,        
        'search_scope': livres,
        'form': form,
       
        
    }
            
    return render(request , 'reservation/form_reservation.html' , context)


@login_required
def trouver_auteur_ou_titre(request):
    query = request.GET.get('q', '').strip()
    livres = Livre.objects.all()
    
    from .forms import ReservationForms
    form = ReservationForms()
    
    aucun_resultat = False

    if query:
       livres_trouves = livres.filter(
           Q(auteur__icontains=query) | Q(titre__icontains=query)
       )
       

       livres_disponibles =[liv for liv in livres_trouves if livre_disponible(liv)]
       if livres_disponibles:
           livres_par_categorie = {"Résultats": livres_disponibles}
       else:
           livres_par_categorie = {}
           aucun_resultat = True
    else:
        categories = Categorie.objects.annotate(nb_livres=Count('livre')).filter(nb_livres__gt=0)
        livres_par_categorie = {}
        
        for cat in categories:
            livres_cat = Livre.objects.filter(categorie=cat)
            livres_disponibles = [liv for liv in livres_cat if livre_disponible(liv)]
            
            if livres_disponibles:
                livres_par_categorie[cat.nom] = livres_disponibles
         
    context = {
        'livres_par_categorie': livres_par_categorie,        
        'query': query,
        'form': form,
        'aucun_resultat': aucun_resultat,
    }

    return render(request, 'reservation/form_reservation.html', context)


def livre_disponible(livre):
   
    emprunts_en_cours = Emprunt.objects.filter(
        livre=livre,
        statut="en_cours"
    ).count()
    
    reservations_actives = Reservation.objects.filter(
        livre=livre,
        statut__in=[
            ReservationStatus.EN_ATTENTE,
            ReservationStatus.CONFIRMEE
        ]
    ).count()

    total_utilise = emprunts_en_cours + reservations_actives

    return total_utilise < livre.quantite


@login_required
def reserver_livre(request, id):
    MAX_EMPRUNTS = 3 
    MAX_RESERVATIONS = 3
    with transaction.atomic():
        livre = get_object_or_404(Livre, id=id)
        
        # 2 — VÉRIFIER RETARDS
        if Emprunt.objects.filter(utilisateur=request.user, statut="retard").exists():
            messages.error(request, "Désolé ! Vous avez des retards. Réservation impossible.")
            return redirect("afficher_page_reservation")

        #3 — VÉRIFIER DISPONIBILITÉ
        if not livre_disponible(livre):
            messages.error(request, "Désolé ! Ce livre n'est plus disponible.")
            return redirect("afficher_page_reservation")

        # 4 — UTILISATEUR A DÉJÀ RÉSERVÉ CE LIVRE ?
        deja_reserve = Reservation.objects.filter(
            utilisateur=request.user,
            livre=livre,
            statut__in=[ReservationStatus.EN_ATTENTE, ReservationStatus.CONFIRMEE]
        ).exists()
        
        if deja_reserve:
            messages.error(request , "Désolé ! Vous avez déjà une réservation active pour ce livre")
            return redirect("afficher_page_reservation")

        #5 — LIMITE MAX DE RÉSERVATIONS
        nb_reservations =  Reservation.objects.filter(
            utilisateur=request.user,
            statut__in=[ReservationStatus.EN_ATTENTE, ReservationStatus.CONFIRMEE]
        ).count() 
        
        
        #Le membre ne peut pas avoir plus de 3 reservations en cours
        if nb_reservations >= MAX_RESERVATIONS:
            messages.error(request , "Désolé! Vous avez déjà atteint 3 réservations en cours alors vous ne pouvez pas faire de réservation")
            return redirect("afficher_page_reservation")
        
        
        #Le membre ne peut pas avoir plus de 3 emprunts en cours
        nb_emprunts = Emprunt.objects.filter(utilisateur = request.user , statut = "en_cours").count()
        
        if nb_emprunts >= MAX_EMPRUNTS:
            messages.error(request , "Désolé! Vous avez déjà atteint 3 emprunts en cours alors vous ne pouvez pas faire de réservation")
            return redirect("afficher_page_reservation")
        
        
        if Reservation.est_expire:
            Reservation.statut = ReservationStatus.ANNULEE

        #6 — TRAITEMENT FORMULAIRE AVEC DJANGO ModelForm
        if request.method == "POST":
            form = ReservationForms(request.POST)
            if form.is_valid():
                reservation = form.save(commit=False)
                reservation.utilisateur = request.user            
                reservation.livre = livre
                reservation.type_reservation = "physique"
                reservation.statut = ReservationStatus.EN_ATTENTE
                reservation.message_utilisateur = form.cleaned_data.get("message_utilisateur", "")
                reservation.confirme = False
                reservation.save()                

                messages.success(request, "Votre demande de réservation est envoyée.")
                return redirect("mes_reservations")

            else:
                messages.error(request, "Erreur dans le formulaire.")

        
        return redirect("afficher_page_reservation")

        
#detail sur une resservation précise d'un utilisateur

@login_required
def detail_reservation(request , id):
    reservation = get_object_or_404(Reservation , id = id , utilisateur = request.user)
    context = {
        
        "reservation" : reservation
    }
    
    return render (request , 'reservation/detail_reservation.html' , context)
    
    
@login_required
def mes_reservations(request):
    reservations = Reservation.objects.filter(utilisateur = request.user).order_by('-date_reservation')
    context = {
        'reservations' : reservations
    }
    
    return render(request , 'reservation/mes_reservations.html' , context)


@login_required
def annuler_reservation(request, id):
    try:
        reservation = Reservation.objects.get(id=id, utilisateur=request.user)
    except Reservation.DoesNotExist:
        messages.error(request, "Réservation introuvable")
        return redirect("mes_reservations")

    if reservation.statut != "en_attente":   
        messages.error(request, "Action impossible")
        return redirect("mes_reservations")

    reservation.statut = "annulee"
    reservation.save()
    messages.success(request, "Votre réservation a été annulée avec succès.")
    return redirect("mes_reservations")    

@login_required
def gestion_reservations(request):
    statut = request.GET.get('statut' , ReservationStatus.EN_ATTENTE)
    reservations = Reservation.objects.filter(statut-statut).order_by('-date_reservation')
    
    context = {
        'statut' : statut,
        'reservations' : reservations,
        'statuts': ReservationStatus
    }
    
    return render (request , 'reservation/gestion_reservations.html' , context) 

@login_required
def confirmer_reservation(request , id):
    reservation = get_object_or_404(Reservation , id = id)
    
    if reservation.statut != ReservationStatus.EN_ATTENTE:
        messages.warning(request , "Cette réservation n'est pas en attente et peut donc pas être confirmée")
        
    reservation.statut = ReservationStatus.CONFIRMEE
    reservation.date_confirmation = date.today()
    reservation.save()
    
    messages.success(request , "Réservation confirmée avec succès")
    return redirect('gestion_reservations')

@login_required
def rejeter_reservation(request , id):
    reservation = get_object_or_404(Reservation , id = id)
    
    if reservation.statut not in [ReservationStatus.EN_ATTENTE , ReservationStatus.CONFIRMEE]:
        messages.warning(request , "Vous ne pouvez rejeter que les réservations en attente ou confirmées")
        return redirect('gestion_reservations')
    
    reservation.statut = ReservationStatus.ANNULEE
    reservation.save()
    messages.success(request , "Réservation rejetée avec succès")
    
@login_required
def liste_reservations(request):
    reservations = (Reservation.objects.filter(statut= ReservationStatus.EN_ATTENTE).select_related("livre" , "utilisateur").order_by('-date_reservation'))
    
    context = {
        'reservations' : reservations
    }
    return render(request , 'reservation/liste_reservations.html' , context)
    

@login_required
def reservation_detail_ajax(request, reservation_id):
    reservation = get_object_or_404(
        Reservation.objects.select_related("livre", "utilisateur"),
        id=reservation_id
    )

    a_retard = Emprunt.objects.filter(
        utilisateur=reservation.utilisateur,
        statut="retard"
    ).exists()

    nb_reservations = Reservation.objects.filter(
        utilisateur=reservation.utilisateur,
        statut=ReservationStatus.EN_ATTENTE
    ).exclude(id=reservation.id).count()

    doublon = Reservation.objects.filter(
        utilisateur=reservation.utilisateur,
        livre=reservation.livre,
        statut=ReservationStatus.EN_ATTENTE
    ).exclude(id=reservation.id).exists()

    image_url = reservation.livre.couverture.url if reservation.livre.couverture else "/static/img/book_placeholder.png"

    data = {
        "livre": {
            "titre": reservation.livre.titre,
            "image": image_url
        },
        "membre": {
            "nom": reservation.utilisateur.get_full_name(),
            "email": reservation.utilisateur.email
        },
        "date_reservation": reservation.date_reservation.strftime("%d/%m/%Y %H:%M"),
        "message": reservation.message_utilisateur or "Aucun message",
        "criteres": {
            "retard": not a_retard,
            "disponible": True,   
            "doublon": not doublon,
            "limite": nb_reservations < 3,
            "type": reservation.get_type_reservation_display()
        }
    }

    return JsonResponse(data)


@login_required
def telecharger_pdf_reservation(request , id):
    reservation = get_object_or_404(Reservation , id = id)
    
    pdf_buffer = generer_pdf_qr(reservation)
    response = HttpResponse(pdf_buffer.getvalue() , content_type = 'application/pdf')
    
    response['Content-Disposition'] = (f'attachment; filename="reservation_{reservation.id}.pdf"' )
    
    return response