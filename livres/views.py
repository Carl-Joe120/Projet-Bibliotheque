from django.contrib import messages
from django.shortcuts import redirect , get_object_or_404
import csv
import json
from django.db.models.functions import TruncMonth
from utilisateurs.views import is_super_administrateur
from .utils import importer_livres
from django.contrib.auth.decorators import login_required , user_passes_test
from django.http import HttpRequest , JsonResponse , HttpResponse
from reservation.models import Reservation , ReservationStatus
from django.db.models import Sum
from livres.models import Livre , Emprunt , EmpruntType , Categorie
from datetime import date, timedelta
from django.views.decorators.http import require_POST , require_http_methods
from django.db import transaction
from django.shortcuts import render
from .models import Favori, Livre , ObjectifLecture
from .services import verifier_retards_et_envoyer_notifications
from django.utils import timezone
from utilisateurs.models import Role , Utilisateur
from .forms import LivreForm
from django.db.models import Q , Count , Avg
from django.core.paginator import Paginator
from utilisateurs.utils import log_activity
from utilisateurs.utils import permission_requise


def importer_livre_français(request):
    total_imported, google_used = importer_livres()
    messages.success(request, f"{total_imported} livres importés avec succès.")
    if google_used > 0:
        messages.info(request, f"{google_used} livres ont été complétés avec Google Books API.")
    return redirect('list_livres')

@login_required
def livre_empruntes_membres(request):
    emprunts = Emprunt.objects.filter(
        utilisateur=request.user,
        statut=EmpruntType.EN_COURS
    ).select_related("livre")

    context = {
        "emprunts": emprunts
    }

    return render(request, 'livres/livres_empruntes.html', context)

def is_secretaire(user):
    return user.role == Role.Secretaire


@login_required
def liste_livres_secretaire(request):
    livres = Livre.objects.all().order_by('-date_ajout_livre')

    # Calculer les statistiques
    categories_count = Livre.objects.values('categorie').distinct().count()
    total_quantity = Livre.objects.aggregate(total=Sum('quantite'))['total'] or 0

    context = {
        'livres': livres,
        'categories_count': categories_count,
        'total_quantity': total_quantity
    }
    return render(request, 'livres/liste_livres_secretaire.html', context)


@login_required
@user_passes_test(is_secretaire)
@permission_requise("ajouter_livre")
def ajouter_livre(request):
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            livre = form.save()
            
            log_activity(request , "CREATE" , f"Livre ajouté : « {livre.titre} » par {livre.auteur}")
            messages.success(request, "Livre ajouté avec succès !")
            return redirect('liste_livres_secretaire')
    else:
        form = LivreForm()
    context = {
        'form': form
    }
    return render(request, 'livres/ajouter_livre.html', context)




@login_required
@user_passes_test(is_secretaire)
@permission_requise("modifier_livre")
def modifier_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    if request.method == "POST":
        form = LivreForm(request.POST, request.FILES, instance=livre)
        if form.is_valid():
            form.save()
            
            log_activity(request , "UPDATE" , f"Livre modifié : « {livre.titre} » par {livre.auteur}")
            messages.success(request, "Livre modifié avec succès !")
            return redirect('liste_livres_secretaire')
    else:
        form = LivreForm(instance=livre)
    return render(request, 'livres/modifier_livre.html', {'form': form, 'livre': livre})

# ----------------------------------------
# Supprimer un livre
# ----------------------------------------

@login_required
@user_passes_test(is_secretaire)
@permission_requise("supprimer_livre")
def supprimer_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)

    if request.method == "POST":
        titre = livre.titre
        livre.delete()
        
        log_activity(request , "DELETE" , f"Livre supprimé : « {titre} »")
        
        messages.success(request, f"Le livre '{titre}' a été supprimé avec succès.")
        return redirect('liste_livres_secretaire')

    messages.warning(request, "Action non autorisée.")
    return redirect('liste_livres_secretaire')
    
    
    
    
@login_required
def gestion_retards_membre(request: HttpRequest):
    
    retards = Emprunt.objects.filter(utilisateur = request.user , statut = EmpruntType.EN_COURS , date_retour_effectif__isnull = True , date_retour_prevu__lt = date.today()).select_related("livre")
    
    for emprunts in retards:
        emprunts.jours_retards = (date.today() - emprunts.date_retour_prevu).days
        
    context = {
        "retards" : retards
    }
    
    return render(request , 'livres/gestion_retards.html' , context)

@login_required
def gestion_retards_par_secretaire(request: HttpRequest):
    # Récupérer tous les emprunts en retard
    retards = Emprunt.objects.filter(
        statut=EmpruntType.EN_COURS,
        date_retour_effectif__isnull=True,
        date_retour_prevu__lt=date.today()
    ).select_related("livre", "utilisateur").order_by('-date_retour_prevu')

    # Calculer les jours de retard et les statistiques
    total_retards = retards.count()
    jours_retard_total = 0

    for emprunt in retards:
        jours_retard = (date.today() - emprunt.date_retour_prevu).days
        emprunt.jours_retard = jours_retard
        jours_retard_total += jours_retard

    # Statistiques supplémentaires
    retards_graves = retards.filter(date_retour_prevu__lt=date.today() - timedelta(days=7)).count()
    retards_recents = retards.filter(date_retour_prevu__gte=date.today() - timedelta(days=3)).count()

    context = {
        "retards": retards,
        "total_retards": total_retards,
        "jours_retard_total": jours_retard_total,
        "retards_graves": retards_graves,
        "retards_recents": retards_recents,
        "moyenne_retard": round(jours_retard_total / total_retards, 1) if total_retards > 0 else 0
    }

    return render(request, 'livres/gestion_retards_secretaire.html', context)


def est_secretaire(user):
    return user.is_authenticated and user.role == "secretaire"


@login_required
@user_passes_test(est_secretaire, login_url='loginview')
@permission_requise("valider_emprunt")
def valider_retrait(request, id):

    if request.method != "POST":
        return redirect("gestion_reservations")

    reservation = get_object_or_404(Reservation, id=id)

    # BLOKE SI DEJA TRAITE
    if reservation.statut == ReservationStatus.TRANSFORMEE:
        messages.warning(request, "Cette réservation a déjà été traitée.")
        return redirect('scan_qr', token=reservation.qr_token)

    if reservation.statut == ReservationStatus.ANNULEE:
        messages.warning(request, "Réservation annulée.")
        return redirect('scan_qr', token=reservation.qr_token)

    action = request.POST.get("action")

    # ======================
    # ✔ VALIDER EMPRUNT
    # ======================
    if action == "emprunt":

        livre = reservation.livre

        if livre.quantite <= 0:
            messages.error(request, "Livre indisponible.")
            return redirect('scan_qr', token=reservation.qr_token)

        with transaction.atomic():

            Emprunt.objects.create(
                utilisateur=reservation.utilisateur,
                livre=livre,
                valide_par=request.user
            )

            livre.quantite -= 1
            livre.save()

            reservation.statut = ReservationStatus.TRANSFORMEE
            reservation.save()

            log_activity(
                request,
                "EMPRUNT",
                f"{reservation.utilisateur.username} a emprunté {livre.titre}"
            )

        messages.success(request, "Retrait validé avec succès.")
        return redirect('gestion_reservations')

    # ======================
    # ❌ ANNULER
    # ======================
    elif action == "annuler":

        reservation.statut = ReservationStatus.ANNULEE
        reservation.save()

        log_activity(
            request,
            "RESERVATION",
            f"Réservation annulée par {request.user.username}"
        )

        messages.success(request, "Réservation annulée.")
        return redirect('gestion_reservations')

    return redirect('scan_qr', token=reservation.qr_token)    
  
@login_required
@user_passes_test(is_secretaire)
@permission_requise("gestion_emprunts")
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


@login_required
def voir_nouveaute_livre(request):

    limite = timezone.now() - timedelta(days=30)

    Livre.objects.filter(
        est_nouveau=True,
        date_ajout_livre__lt=limite
    ).update(est_nouveau=False)

    livres = Livre.objects.filter(est_nouveau=True)

    return render(
        request,
        "livres/nouveautes.html",
        {"livres": livres}
    )
    

@login_required
def liste_emprunts_en_cours_secretaire(request):
    
    emprunts = Emprunt.objects.filter(
        statut=EmpruntType.EN_COURS
    ).select_related(
        "livre",
        "utilisateur",
        "valide_par"
    ).order_by("-date_emprunt")

    today = date.today()
    
    # Count loans overdue
    retards_count = Emprunt.objects.filter(
        statut=EmpruntType.EN_COURS,
        date_retour_prevu__lt=today
    ).count()
    
    # Count loans due within next 3 days
    soon_overdue_count = Emprunt.objects.filter(
        statut=EmpruntType.EN_COURS,
        date_retour_prevu__range=[today, today + timedelta(days=3)]
    ).count()

    context = {
        "emprunts": emprunts,
        "total_emprunts": emprunts.count(),
        "retards_count": retards_count,
        "soon_overdue_count": soon_overdue_count
    }

    return render(request, "livres/gestion_emprunt_secretaire.html", context )
    


    
@login_required
@user_passes_test(is_secretaire)
def gestion_des_retours(request):
   

    emprunts = Emprunt.objects.filter(
        statut='en_cours'
    ).select_related('livre', 'utilisateur')

    selected_id = request.GET.get('emprunt_id')
    emprunt_selectionne = None

    if selected_id:
        emprunt_selectionne = Emprunt.objects.get(id=selected_id)

    return render(request, 'livres/gestion_retours.html', {
        'emprunts': emprunts,
        'emprunt': emprunt_selectionne
    })
   
    



@login_required
@user_passes_test(is_super_administrateur)
def gestion_livres_admin(request):

    query = request.GET.get('q')
    filtre_dispo = request.GET.get('dispo')
    filtre_categorie = request.GET.get('categorie')

    livres = Livre.objects.select_related('categorie').all()

    
    if query:
        livres = livres.filter(
            Q(titre__icontains=query) |
            Q(auteur__icontains=query)
        )

    
    if filtre_dispo in ['disponible', 'indisponible']:
        if filtre_dispo == 'disponible':
            livres = livres.filter(quantite__gt=0)
        else:
            livres = livres.filter(quantite=0)

    
    if filtre_categorie and filtre_categorie.isdigit():
        livres = livres.filter(categorie_id=int(filtre_categorie))

    livres = livres.order_by('-date_ajout_livre')

    paginator = Paginator(livres, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'query': query or '',
        'total_livres': livres.count(),
        'categories': Categorie.objects.all(),
        'filtre_dispo': filtre_dispo or '',
        'filtre_categorie': filtre_categorie or ''
    }

    return render(request, 'livres/liste_livres_admin.html', context)


@login_required
@user_passes_test(is_super_administrateur)
def statistiques_admin(request):

    # ========================
    # KPI GLOBAL
    # ========================
    total_livres = Livre.objects.count()
    total_categories = Categorie.objects.count()
    total_emprunts = Emprunt.objects.count()

    livres_disponibles = Livre.objects.filter(quantite__gt=0).count()
    livres_indisponibles = Livre.objects.filter(quantite=0).count()

    emprunts_en_cours = Emprunt.objects.filter(statut='en_cours').count()
    emprunts_retournes = Emprunt.objects.filter(statut='retourne').count()

    emprunts_retard = Emprunt.objects.filter(
        date_retour_effectif__isnull=True,
        date_retour_prevu__lt=date.today()
    ).count()

    # ========================
    # GRAPH 1 : LIVRES PAR CATEGORIE
    # ========================
    categories_data = (
        Livre.objects.values('categorie__nom')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    labels_cat = [c['categorie__nom'] or "Sans catégorie" for c in categories_data]
    data_cat = [c['total'] for c in categories_data]

    # ========================
    # GRAPH 2 : EMPRUNTS 7 DERNIERS JOURS
    # ========================
    last_7_days = []
    emprunts_par_jour = []

    for i in range(7):
        day = date.today() - timedelta(days=i)
        count = Emprunt.objects.filter(date_emprunt=day).count()
        last_7_days.append(day.strftime("%d/%m"))
        emprunts_par_jour.append(count)

    last_7_days.reverse()
    emprunts_par_jour.reverse()

    context = {
        # KPI
        'total_livres': total_livres,
        'total_categories': total_categories,
        'total_emprunts': total_emprunts,
        'livres_disponibles': livres_disponibles,
        'livres_indisponibles': livres_indisponibles,
        'emprunts_en_cours': emprunts_en_cours,
        'emprunts_retournes': emprunts_retournes,
        'emprunts_retard': emprunts_retard,

        # Charts
        'labels_cat': labels_cat,
        'data_cat': data_cat,
        'labels_days': last_7_days,
        'data_days': emprunts_par_jour,
    }

    return render(request, 'livres/statistiques.html', context)


@login_required
def historique_emprunt_membre(request):
    emprunts = Emprunt.objects.filter(utilisateur = request.user).select_related('livre').order_by('-date_emprunt')
    
    context = {
        'emprunts': emprunts
    }
    
    return render(request , 'livres/historique_membre.html ', context)


@login_required
def mes_favoris(request):
    favoris = Favori.objects.filter(utilisateur = request.user).select_related('livre')
    
    return render(request , 'livres/favoris.html'  , {'favoris' : favoris})

@login_required
def analyse_lecture(request):
  
    user = request.user

    # Total emprunts actifs
    emprunt_actif = Emprunt.objects.filter(utilisateur=user, statut=EmpruntType.EN_COURS).count()

    total = Emprunt.objects.filter(utilisateur=user).count()

    reste_objectif = max(0, 12 - total)
    
    # Données mensuelles pour le graphique
    par_mois = (
        Emprunt.objects.filter(utilisateur=user)
        .annotate(month=TruncMonth('date_emprunt'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = [item['month'].strftime('%b %Y') if item['month'] else 'N/A' for item in par_mois]
    data = [item['count'] for item in par_mois]

    # Nombre de catégories explorées
    categories_count = (
        Emprunt.objects.filter(utilisateur=user)
        .exclude(livre__categorie__isnull=True)
        .values('livre__categorie')
        .distinct()
        .count()
    )

    # Moyenne mensuelle
    monthly_avg = 0
    if par_mois:
        total_months = len(par_mois)
        if total_months > 0:
            monthly_avg = round(sum(data) / total_months, 1)
    # Répartition par catégories
    categories_stats = (
        Emprunt.objects.filter(utilisateur=user)
        .exclude(livre__categorie__isnull=True)
        .values('livre__categorie__nom')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    categories_labels = [item['livre__categorie__nom'] for item in categories_stats]
    categories_data = [item['count'] for item in categories_stats]

    # Série actuelle (simplifié - jours depuis dernier emprunt)
    current_streak = 0
    dernier_emprunt = Emprunt.objects.filter(utilisateur=user).order_by('-date_emprunt').first()
    if dernier_emprunt:
        jours_depuis_dernier = (date.today() - dernier_emprunt.date_emprunt).days
        if jours_depuis_dernier <= 7:  # Considère comme actif si emprunt récent
            current_streak = max(1, 7 - jours_depuis_dernier)

    # Emprunts ce mois-ci
    mois_actuel = date.today().month
    annee_actuelle = date.today().year
    emprunts_mois = Emprunt.objects.filter(
        utilisateur=user,
        date_emprunt__month=mois_actuel,
        date_emprunt__year=annee_actuelle
    ).count()

    # Retours ce mois-ci
    retours_mois = Emprunt.objects.filter(
        utilisateur=user,
        date_retour_effectif__month=mois_actuel,
        date_retour_effectif__year=annee_actuelle
    ).count()

    # Retards actifs
    retards_actuels = Emprunt.objects.filter(
        utilisateur=user,
        statut=EmpruntType.EN_COURS,
        date_retour_prevu__lt=date.today()
    ).count()

    return render(request, 'livres/analyse.html', {
        'total': total, 
        
        'reste_objectif': reste_objectif,
        'emprunt_actif': emprunt_actif,
        'emprunts_mois': emprunts_mois,
        'retours_mois': retours_mois,
        'retards_actuels': retards_actuels,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'categories_count': categories_count,
        'monthly_avg': monthly_avg,
        'current_streak': current_streak,
        #'next_goal': next_goal,
        'categories_labels': json.dumps(categories_labels),
        'categories_data': json.dumps(categories_data),
    })


@login_required
def objectifs_annuels(request):
    annee_actuelle = date.today().year

    # Récupération ou création de l'objectif
    obj, created = ObjectifLecture.objects.get_or_create(
        utilisateur=request.user,
        anne=annee_actuelle
    )

    if request.method == 'POST':
        # Trete valè form lan
        nouvel_objectif = request.POST.get('objectif')
        if nouvel_objectif:
            try:
                obj.objectif = int(nouvel_objectif)
                obj.save()
                return redirect('objectifs_annuels')  # refresh page pou wè nouvo valè
            except ValueError:
                messages.error(request , "veuillez rentrer un nombre valide pour l'objectif")
    total_lus = Emprunt.objects.filter(
        utilisateur=request.user,
        statut='retourne'
    ).count()

    progression = int((total_lus / obj.objectif) * 100) if obj.objectif else 0
    if progression > 100:
        progression = 100

    restant = max(0, obj.objectif - total_lus) if obj.objectif else 0

    return render(request, 'livres/objectifs.html', {
        'objectif': obj.objectif,
        'total_lus': total_lus,
        'progression': progression,
        'restant': restant
    })


@login_required
def toggle_favori(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    
    favori, created = Favori.objects.get_or_create(utilisateur=request.user, livre=livre)
    messages.success(request , f"Le livre '{livre.titre}' a été {'ajouté à' if created else 'retiré de'} vos favoris.")
    
    if not created:
        favori.delete()
        
    return redirect(request.META.get('HTTP_REFERER', 'mes_favoris'))

@login_required
def marquer_retour(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, id=emprunt_id)
    emprunt.statut = EmpruntType.RETOURNE
    emprunt.date_retour_effectif = timezone.now()
    emprunt.save()
    messages.success(request, f"Le retour de '{emprunt.livre.titre}' a été validé.")
    return redirect('gestion_des_retours')



@login_required
def analyse_rapports(request):
    

    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    categorie = request.GET.get('categorie', '')
    statut = request.GET.get('statut', '')

    stats = get_global_stats()
    

    emprunts_recents = get_emprunts_recents(date_start, date_end, statut, categorie)
    stats_categories = get_stats_categories()

    context = {
        'stats': stats,
        'emprunts_recents': emprunts_recents,
        'stats_categories': stats_categories,
        'categories': Categorie.objects.all(),
        'date_start': date_start,
        'date_end': date_end,
        'statut': statut,
        'categorie': categorie,
    }

    

    return render(request, 'livres/analayse_rapports.html', context)


def get_global_stats():
    try:
        total_livres = Livre.objects.count()
        livres_disponibles = Livre.objects.filter(quantite__gt=0).count()
        emprunts_actifs = Emprunt.objects.filter(statut='en_cours').count()
        reservations = Reservation.objects.filter(statut='en_attente').count()

        

        return {
            'total_livres': total_livres,
            'livres_disponibles': livres_disponibles,
            'emprunts_actifs': emprunts_actifs,
            'reservations': reservations,
        }

    except Exception as e:
        print("ERREUR 👉", e)
        return {
            'total_livres': 0,
            'livres_disponibles': 0,
            'emprunts_actifs': 0,
            'reservations': 0,
        }


def get_emprunts_recents(date_start='', date_end='', statut='', categorie='', limit=100):
    from datetime import datetime

    try:
        emprunts = Emprunt.objects.select_related('livre', 'utilisateur').order_by('-date_emprunt')

        # ✅ FILTRE DATE START
        if date_start:
            try:
                date_start = datetime.strptime(date_start, "%Y-%m-%d").date()
                emprunts = emprunts.filter(date_emprunt__gte=date_start)
            except:
                pass

        # ✅ FILTRE DATE END
        if date_end:
            try:
                date_end = datetime.strptime(date_end, "%Y-%m-%d").date()
                emprunts = emprunts.filter(date_emprunt__lte=date_end)
            except:
                pass

        # ✅ FILTRE STATUT
        if statut:
            emprunts = emprunts.filter(statut=statut)

        # ✅ FILTRE CATEGORIE
        if categorie:
            try:
                emprunts = emprunts.filter(livre__categorie_id=int(categorie))
            except:
                pass

        emprunts = emprunts[:limit]

        data = []
        for e in emprunts:
            data.append({
                'id': e.id,
                'livre': e.livre.titre if e.livre else 'N/A',
                'utilisateur': e.utilisateur.get_full_name() if e.utilisateur else 'N/A',
                'date_emprunt': e.date_emprunt,
                'date_retour_prevue': e.date_retour_prevu,
                'statut': e.statut,
                'en_retard': e.en_retard(),
            })

        return data

    except Exception as e:
        print(f"Erreur: {e}")
        return []


def get_stats_categories():
    try:
        categories = Categorie.objects.annotate(
            total_livres=Count('livre'),
            emprunts_actifs=Count('livre__emprunt', filter=Q(livre__emprunt__statut='en_cours')),
            reservations=Count('livre__reservation')
        )

        data = []
        for cat in categories:
            disponibles = cat.total_livres - cat.emprunts_actifs
            taux = (cat.emprunts_actifs / cat.total_livres * 100) if cat.total_livres else 0

            data.append({
                'nom': cat.nom,
                'total_livres': cat.total_livres,
                'disponibles': disponibles,
                'emprunts_actifs': cat.emprunts_actifs,
                'reservations': cat.reservations,
                'taux_utilisation': round(taux, 2),
            })

        return data
    except Exception as e:
        print(e)
        return []


@require_http_methods(["GET"])
def export_csv_rapports(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rapport.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Livre', 'Utilisateur', 'Date', 'Retour', 'Statut'])

    for e in get_emprunts_recents(limit=1000):
        writer.writerow([
            e['id'],
            e['livre'],
            e['utilisateur'],
            e['date_emprunt'],
            e['date_retour_prevue'],
            e['statut'],
        ])

    return response
@require_http_methods(["GET"])
def get_data_chart_emprunts(request):
    """
    API pour retourner les données graphique des emprunts
    Format JSON pour Chart.js
    """
    try:
        data = get_emprunts_par_mois()
        
        return JsonResponse({
            'labels': list(data.keys()),
            'datasets': [
                {
                    'label': 'Emprunts',
                    'data': list(data.values()),
                    'borderColor': '#1976d2',
                    'backgroundColor': 'rgba(25, 118, 210, 0.1)',
                    'borderWidth': 2,
                    'tension': 0.4,
                }
            ]
        })
    except Exception as e:
        print(f"Erreur get_data_chart_emprunts: {e}")
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_data_chart_categories(request):
    """
    API pour retourner les données graphique des catégories
    Format JSON pour Chart.js
    """
    try:
        stats = get_stats_categories()
        
        labels = [s['nom'] for s in stats]
        data = [s['total_livres'] for s in stats]
        
        colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c',
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
        ]
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Livres par Catégorie',
                    'data': data,
                    'backgroundColor': colors[:len(labels)],
                    'borderColor': '#fff',
                    'borderWidth': 2,
                }
            ]
        })
    except Exception as e:
        print(f"Erreur get_data_chart_categories: {e}")
        return JsonResponse({'error': str(e)}, status=400)

def filtrer_emprunts(date_start='', date_end='', categorie='', statut=''):
    """
    Filtre les emprunts selon critères
    
    Args:
        date_start (str): Date début YYYY-MM-DD
        date_end (str): Date fin YYYY-MM-DD
        categorie (str): ID de la catégorie
        statut (str): Statut de l'emprunt
    
    Retourne: QuerySet filtré
    """
    try:
        emprunts = Emprunt.objects.select_related('livre', 'utilisateur')
        
        if date_start:
            try:
                start = datetime.strptime(date_start, '%Y-%m-%d').date()
                emprunts = emprunts.filter(date_emprunt__gte=start)
            except ValueError:
                pass
        
        if date_end:
            try:
                end = datetime.strptime(date_end, '%Y-%m-%d').date()
                emprunts = emprunts.filter(date_emprunt__lte=end)
            except ValueError:
                pass
        
        if categorie:
            emprunts = emprunts.filter(livre__categorie_id=categorie)
        
        if statut:
            emprunts = emprunts.filter(statut=statut)
        
        return emprunts.order_by('-date_emprunt')
    except Exception as e:
        print(f"Erreur filtrer_emprunts: {e}")
        return Emprunt.objects.none()


# ============================================================================
# FONCTIONS POUR GÉNÉRER PDF (si vous utilisez weasyprint ou reportlab)
# ============================================================================
@login_required
def generate_pdf_rapport(request):
    """
    Génère un rapport PDF
    Nécessite: pip install weasyprint ou pip install reportlab
    """
    try:
        # Option 1: Avec weasyprint (recommandé)
        from weasyprint import HTML
        
        context = {
            'stats': get_global_stats(),
            'emprunts_recents': get_emprunts_recents(limit=50),
            'stats_categories': get_stats_categories(),
        }
        
        html_string = render_to_string('livres/rapport_pdf.html', context)
        html = HTML(string=html_string)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="rapport_bibliotheque.pdf"'
        
        html.write_pdf(response)
        return response
        
    except ImportError:
        print("weasyprint non installé. Utiliser: pip install weasyprint")
        return HttpResponse("Erreur: weasyprint non installé", status=400)
    except Exception as e:
        print(f"Erreur generate_pdf_rapport: {e}")
        return HttpResponse(f"Erreur: {e}", status=400)



