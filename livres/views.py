from django.contrib import messages
from django.shortcuts import redirect
from .utils import importer_livres
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from reservation.models import Reservation , ReservationStatus
from django.shortcuts import get_object_or_404
from livres.models import Livre , Emprunt , EmpruntType
from datetime import date

from django.shortcuts import render
from .models import Livre

def importer_livre_français(request):
    total_imported, google_used = importer_livres()
    messages.success(request, f"{total_imported} livres importés avec succès.")
    if google_used > 0:
        messages.info(request, f"{google_used} livres ont été complétés avec Google Books API.")
    return redirect('list_livres')

@login_required
def livre_empruntes(request):
    return render(request , 'livres/livres_empruntes.html')

@login_required
def gestion_emprunts(request: HttpRequest):
    return render(request , 'livres/gestion_emprunts.html')

@login_required
def gestion_retours(request: HttpRequest):
    return render(request , 'livres/gestion_retours.html')

@login_required
def gestion_retards(request: HttpRequest):
    return render(request , 'livres/gestion_retards.html')

@login_required
def transformer_en_emprunt(request: HttpRequest , id):
    reservation = get_object_or_404(Reservation , id = id)
    
    if reservation.statut != ReservationStatus.CONFIRMEE:
        messages.error(request , "Seules les réservations confirmées peuvent être transformées en emprunts")
        return redirect('reservation:gestion_reservations')
    
    livre = reservation.livre
    
    if livre.quantite <= 0:
        messages.error(request , "Le livre n'est pas disponible pour l'emprunt")
        return redirect('reservation:gestion_reservations')
    
    Emprunt.objects.create(
        utilisateur = reservation.utilisateur,
        livre = reservation.livre
    )
    
    livre.quantite -= 1
    livre.save()
    
    reservation.statut = ReservationStatus.TRANSFORMEE
    reservation.save()
    
    messages.success(request , "Réservation transformée en emprunt avec succès")
    return redirect ('reservation:gestion_reservations')

@login_required
def gestion_emprunts(request):
    
    Emprunt.objects.filter(
        statut = EmpruntType.EN_COURS ,
        date_retour_prevu__lt = date.today(),
        date_retour_effectif__isnull = True        
    ).update(statut = EmpruntType.RETARD)
    
    statut = request.GET.get('statut' , EmpruntType.EN_COURS)
    
    emprunts = Emprunt.objects.filter(statut=statut).select_related('utilisateur' , 'livre')
    
    context = {
        'statut' : statut,
        'emprunts' : emprunts,
        'statuts' : EmpruntType
    }
    
    return render (request , 'livres/gestions_emprunts.html' , context)

@login_required
def marquer_retour(request , id):
    emprunt = get_object_or_404(Emprunt , id = id)
    
    if emprunt.statut != EmpruntType.EN_COURS:
        messages.error(request , "Seuls les emprunts en cours peuvent être marqués comme retournés")
        return redirect('gestion_emprunts')
    
    
    livre = emprunt.livre
    
    livre.quantite += 1
    livre.save()
    
    
    emprunt.statut = EmpruntType.RETOURNE
    emprunt.date_retour_effectif = date.today()
    emprunt.save()
    messages.success(request , "Livre marqué comme retourné")
    return redirect('gestion_emprunts')

@login_required
def signaler_retard(request , id):
    emprunt = get_object_or_404(Emprunt , id = id)
    
    if emprunt.statut == EmpruntType.RETOURNE:
        messages.error(request , "Vous pouvez pas signaler ce livre pour retard car il est déjà retourné")
        return redirect('gestion_emprunts')
    
    if not emprunt.en_retard():
        messages.info(request , "Cet emprunt n'est pas encore en retard")
        return redirect('gestion_emprunts')
    
    emprunt.statut = EmpruntType.RETARD
    emprunt.save()
    
    messages.error(request , "Emprunt marqué comme retard")
    return redirect('gestion_emprunts')

