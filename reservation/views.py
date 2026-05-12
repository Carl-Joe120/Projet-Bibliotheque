from django.shortcuts import render , get_object_or_404 , redirect
from django.http import HttpRequest , HttpResponse , JsonResponse , FileResponse
from livres.models import Livre , Categorie , Emprunt , Favori
from livres.views import is_secretaire
import utilisateurs
from .models import Reservation , ReservationStatus
from utilisateurs.models import Utilisateur
from datetime import date
from django.db.models import Count , Q 
from django.contrib.auth.decorators import login_required , user_passes_test
from .forms import ReservationForms
from django.contrib import messages
from django.template.loader import render_to_string
import pdfkit
from django.db import transaction
from .utils import generer_pdf_qr
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from utilisateurs.utils import log_activity, permission_requise

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
            
        favoris_ids = []
        if request.user.is_authenticated:
            favoris_ids = list(Favori.objects.filter(utilisateur = request.user).values_list('livre_id' , flat=True))
            
            
            
    context = {
        'livres_par_categorie': livres_par_categorie,        
        'search_scope': livres,
        'form': form,
        'favoris_ids' : favoris_ids, 
        
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

    if request.method != "POST":
        return redirect("afficher_page_reservation")

    with transaction.atomic():

        livre = get_object_or_404(
            Livre.objects.select_for_update(),
            id=id
        )

        # 1 — Vérifier retard
        if Emprunt.objects.filter(
            utilisateur=request.user,
            statut="retard"
        ).exists():

            messages.error(
                request,
                "Désolé ! Vous avez des retards. Réservation impossible."
            )
            return redirect("afficher_page_reservation")

        # 2 — Vérifier disponibilité
        if not livre_disponible(livre):
            messages.error(
                request,
                "Désolé ! Ce livre n'est plus disponible."
            )
            return redirect("afficher_page_reservation")

        # 3 — Vérifier doublon
        if Reservation.objects.filter(
            utilisateur=request.user,
            livre=livre,
            statut__in=[
                ReservationStatus.EN_ATTENTE,
                ReservationStatus.CONFIRMEE
            ]
        ).exists():

            messages.error(
                request,
                "Vous avez déjà une réservation active pour ce livre."
            )
            return redirect("afficher_page_reservation")

        # 4 — Limite réservations
        nb_reservations = Reservation.objects.filter(
            utilisateur=request.user,
            statut__in=[
                ReservationStatus.EN_ATTENTE,
                ReservationStatus.CONFIRMEE
            ]
        ).count()

        if nb_reservations >= MAX_RESERVATIONS:
            messages.error(
                request,
                "Vous avez déjà atteint la limite de 3 réservations."
            )
            return redirect("afficher_page_reservation")

        # 5 — Limite emprunts
        nb_emprunts = Emprunt.objects.filter(
            utilisateur=request.user,
            statut="en_cours"
        ).count()

        if nb_emprunts >= MAX_EMPRUNTS:
            messages.error(
                request,
                "Vous avez déjà atteint la limite de 3 emprunts."
            )
            return redirect("afficher_page_reservation")

        # 6 — Création réservation
        form = ReservationForms(request.POST)

        if not form.is_valid():
            messages.error(request, "Erreur dans le formulaire.")
            return redirect("afficher_page_reservation")

        reservation = form.save(commit=False)

        reservation.utilisateur = request.user
        reservation.livre = livre
        reservation.type_reservation = "physique"
        reservation.statut = ReservationStatus.EN_ATTENTE
        reservation.message_utilisateur = form.cleaned_data.get(
            "message_utilisateur", ""
        )
        reservation.confirme = False
        log_activity(request, "RESERVATION", "Nouvelle réservation effectuée")
        reservation.save()

        messages.success(
            request,
            "Votre demande de réservation est envoyée."
        )

        return redirect("mes_reservations")
        
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
    with transaction.atomic():
        reservation = get_object_or_404(
            Reservation.objects.select_for_update(),
            id=id,
            utilisateur=request.user
        )

        if reservation.statut == ReservationStatus.ANNULEE:
            messages.warning(request, "Déjà annulée.")
            return redirect("mes_reservations")

        if reservation.statut == ReservationStatus.TRANSFORMEE:
            messages.error(request, "Impossible d'annuler une réservation déjà utilisée.")
            return redirect("mes_reservations")

        # ❌ Retire: livre.quantite += 1 — livre_disponible() konte otomatikman
        reservation.statut = ReservationStatus.ANNULEE
        reservation.save()
        log_activity(request, "ANNULATION", "Réservation annulée")
        messages.success(request, "Réservation annulée avec succès.")

    return redirect("mes_reservations")  

@login_required
@user_passes_test(is_secretaire)
@permission_requise("gestion_reservations")
def gestion_reservations(request):
    statut = request.GET.get('statut' , ReservationStatus.EN_ATTENTE)
    reservations = Reservation.objects.filter(statut=statut).order_by('-date_reservation')
    
    context = {
        'statut' : statut,
        'reservations' : reservations,
        'statuts': ReservationStatus
    }
    
    return render (request , 'reservation/liste_reservations.html' , context) 

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
    
    log_activity(request , "ANNULATION" , f"Réservation #{reservation.id} rejetée par {request.user.username}")
    
    
    messages.success(request , "Réservation rejetée avec succès")
    
@login_required
def liste_reservations(request):
       
    reservations_en_cours = Reservation.objects.filter(
        statut__in=[ReservationStatus.EN_ATTENTE, ReservationStatus.CONFIRMEE]
    ).select_related("livre", "utilisateur").order_by("-date_reservation")

    # Count by status
    count_en_attente = Reservation.objects.filter(
        statut=ReservationStatus.EN_ATTENTE
    ).count()
    
    count_confirmee = Reservation.objects.filter(
        statut=ReservationStatus.CONFIRMEE
    ).count()

    context = {
        "reservations": reservations_en_cours,
        "count_en_attente": count_en_attente,
        "count_confirmee": count_confirmee,
        "total_reservations": reservations_en_cours.count()
    }
    return render(request, "reservation/liste_reservations.html", context)
    

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
def telecharger_recu(request, id):
    reservation = get_object_or_404(
        Reservation,
        id=id,
        utilisateur=request.user
    )

    pdf_buffer = generer_pdf_qr(reservation)

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"reservation_{reservation.id}.pdf"
    )

def est_secretaire(user):
    return user.is_authenticated and user.role == "secretaire"
    
@login_required
@user_passes_test(est_secretaire, login_url='loginview')
def scan_qr(request, token):
    reservation = get_object_or_404(Reservation, qr_token=token)

    # Expiration
    if reservation.est_expire():
        reservation.statut = ReservationStatus.EXPIREE
        reservation.save()
        statut_qr = "expire"
    elif reservation.statut == ReservationStatus.ANNULEE:
        statut_qr = "annule"
    elif reservation.statut == ReservationStatus.TRANSFORMEE:
        statut_qr = "deja_valide"
    else:
        statut_qr = "valide"

    return render(request, "reservation/scan_result.html", {
        "reservation": reservation,
        "statut_qr": statut_qr
    })
    
    
def redirect_scan(request, token):
    
    return redirect("scan_qr", token=token)