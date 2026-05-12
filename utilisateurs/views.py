from multiprocessing import context
import token
from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth import authenticate , login , logout
from django.contrib import messages
from . import forms
from .models import Role , Utilisateur , UserSession , ActivityLog , Permission , generer_numero_membre
from django.contrib.auth.decorators import login_required , user_passes_test , permission_required
from django.http import HttpRequest , HttpResponseForbidden , HttpResponse
from livres.models import Livre , Emprunt , EmpruntType , Favori
from reservation.models import Reservation , ReservationStatus
from django.db.models import Count 
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import date , datetime , timedelta
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.sessions.models import Session
from ipware import get_client_ip 
from .forms import AdminUserCreationForm , SecretaireCreationForm , VerificationCodeForm
from django.db.models import Q , Count , Sum
from django.core.paginator import Paginator
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group
from .forms import SecretaireCreationForm
import json
from .utils import log_activity , has_permission , permission_requise
import csv
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes , force_str
from .tokens import email_verification_token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import random



# Create your views here.


def loginview(request):
    next_url = request.GET.get("next")

    if request.method == "POST":
        form = forms.SigninForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            if not user.email_verified and user.role == Role.Membre:
                messages.error(request, "Veuillez vérifier votre email avant de vous connecter.")
                return render(request, 'utilisateurs/login.html', {'form': form, 'next': next_url})

            
            if not user.is_approved and user.role == Role.Membre:
                messages.error(request, "Votre compte est en attente d'approbation par un administrateur.")
                return render(request, 'utilisateurs/login.html', {'form': form, 'next': next_url})
            login(request, user)
            log_activity(request, "LOGIN", f"Connexion de {user.username}")
            next_url = request.POST.get("next")

            if next_url and next_url != "None":
                
                return redirect(next_url)

            if user.role == Role.Membre:
                return redirect('redirect_to_membre')
            elif user.role == Role.Secretaire:
                return redirect('redirect_to_secretaire')
            elif user.role == Role.Administrateur:
                return redirect('/admin/')
            elif user.role == Role.SuperAdministrateur:
                return redirect('redirect_to_super_administrateur')

        else:
           
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    else:
        form = forms.SigninForm()

    return render(request, 'utilisateurs/login.html', {
        'form': form,
        'next': next_url
    })  
    
def signupview(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST, request.FILES)

        if form.is_valid():
            code = str(random.randint(100000, 999999))

            newUser = Utilisateur.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                role=Role.Membre,
                telephone=form.cleaned_data['telephone'],
                adresse=form.cleaned_data['adresse'],
                photo_profil=request.FILES.get('photo_profil'),
                is_active=False,
                email_verified=False,
                is_approved=False,
                email_verification_code=code,
                code_expiration=timezone.now() + timedelta(minutes=15)
            )

            send_mail(
                subject="Code de vérification - Bibliothèque Michèle Tardieu",
                message=f"""
Bonjour {newUser.username},

Votre code de vérification est :

{code}

Entrez ce code dans l'application pour activer votre compte.

Ce code expire dans 15 minutes.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[newUser.email],
                fail_silently=False
            )

            request.session['verification_user_id'] = newUser.id

            messages.success(
                request,
                "Compte créé avec succès. Vérifiez votre email pour obtenir votre code."
            )

            return redirect('verify_code')

        else:
            messages.error(request, "Veuillez corriger les erreurs.")

    else:
        form = forms.SignupForm()

    return render(request, 'utilisateurs/signup.html', {'form': form})


def verify_code(request):
    user_id = request.session.get('verification_user_id')

    if not user_id:
        messages.error(request, "Session expirée.")
        return redirect('signupview')

    try:
        user = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect('signupview')

    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']

            if user.code_expiration < timezone.now():
                messages.error(request, "Code expiré.")
                return redirect('signupview')

            if user.email_verification_code == code:
                user.email_verified = True
                user.email_verification_code = None
                user.code_expiration = None
                user.save()

                admins = Utilisateur.objects.filter(
                    role__in=[Role.SuperAdministrateur, Role.Secretaire]
                )

                for admin in admins:
                    send_mail(
                        subject="Nouveau membre à approuver",
                        message=f"{user.username} a vérifié son email.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[admin.email],
                        fail_silently=True,
                    )

                del request.session['verification_user_id']

                messages.success(
                    request,
                    "Email vérifié avec succès. Votre compte attend l'approbation d'un administrateur."
                )

                return redirect('loginview')

            else:
                messages.error(request, "Code incorrect.")

    else:
        form = VerificationCodeForm()

    return render(
        request,
        'utilisateurs/verify_code.html',
        {'form': form}
    )
def get_pret_par_mois(queryset):
    return list(
        queryset
        .annotate(month=TruncMonth('date_emprunt'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

def is_administrateur(user):
    return user.role == Role.Administrateur

@login_required
@user_passes_test(is_administrateur , login_url='/')
def redirect_to_admin(request):
    return redirect('admin/')

def is_super_administrateur(user):
    return user.role == Role.SuperAdministrateur

@login_required
@user_passes_test(is_super_administrateur , login_url='/')
def redirect_to_super_administrateur(request: HttpRequest):    
    pret_par_mois = get_pret_par_mois(Emprunt.objects.all())
    activite_json = json.dumps([
        {
            "month": item["month"].strftime("%b %Y"),
            "count": item["count"]
        }
        for item in pret_par_mois
    ])

    context = {
        "total_livres": Livre.objects.count(),
        "total_membres": Utilisateur.objects.filter(role='membre').count(),
        "emprunts_actifs": Emprunt.objects.filter(
            statut=EmpruntType.EN_COURS,
            date_retour_effectif__isnull=True
        ).count(),
        
        "retards": Emprunt.objects.filter(
            statut=EmpruntType.EN_COURS,
            date_retour_prevu__lt=date.today(),
            date_retour_effectif__isnull=True
        ).count(),

        "derniers_utilisateurs": Utilisateur.objects.order_by('-date_joined')[:5],

        "activite": activite_json,

        "users_roles": [
            Utilisateur.objects.filter(role='administrateur').count(),
            Utilisateur.objects.filter(role='secretaire').count(),
            Utilisateur.objects.filter(role='membre').count(),
        ]
    }

    return render(request, 'utilisateurs/administrateur.html', context)

def is_membre(user):
    return user.role == Role.Membre

@login_required
@user_passes_test(is_membre , login_url='/')
def redirect_to_membre(request: HttpRequest):    
    current_user = request.user
    user_loans = Emprunt.objects.filter(utilisateur=current_user, statut=EmpruntType.EN_COURS).count()
    user_reservations = Reservation.objects.filter(
        utilisateur=current_user,
        statut__in=[ReservationStatus.EN_ATTENTE, ReservationStatus.CONFIRMEE]
    ).count()
    retard = Emprunt.objects.filter(
        utilisateur=current_user,
        statut=EmpruntType.EN_COURS,
        date_retour_prevu__lt=date.today(),
        date_retour_effectif__isnull=True
    ).count()
    
    if current_user.last_nouveaute_seen:
        nouveautes_count = Livre.objects.filter(
            date_ajout_livre__gt=current_user.last_nouveaute_seen.date()
        ).count()
        
    else:
        nouveautes_count = Livre.objects.count()
 
    pret_par_mois_raw = get_pret_par_mois(Emprunt.objects.filter(utilisateur=current_user))
    pret_par_mois = json.dumps([
        {
            'month': item['month'].strftime('%b %Y') if item['month'] else '',
            'count': item['count']
        }
        for item in pret_par_mois_raw
    ])
    
    categories_les_plus_lues = list(
        Emprunt.objects.filter(utilisateur = current_user)
        .values('livre__categorie__nom')
        .annotate(count = Count('id'))
        .order_by('-count')[:5]
    )
    
    context = {
        'user_loans' : user_loans,
        'user_reservations' : user_reservations,
        'retard' : retard,
        'pret_par_mois' : pret_par_mois,
        'categories_les_plus_lues' : json.dumps(categories_les_plus_lues),
        'user': current_user,
        'nouveautes_count' : nouveautes_count,
    }   
        
    return render(request , 'utilisateurs/membres.html' , context)

def is_secretaire(user):
    return user.role == Role.Secretaire


@login_required
@user_passes_test(is_secretaire, login_url='loginview')
def redirect_to_secretaire(request: HttpRequest):
    from dateutil.relativedelta import relativedelta

    reservations_en_attente = Reservation.objects.filter(
        statut=ReservationStatus.EN_ATTENTE
    ).count()

    emprunts_en_cours = Emprunt.objects.filter(
        statut=EmpruntType.EN_COURS
    ).count()

    retards = Emprunt.objects.filter(
        statut=EmpruntType.EN_COURS,
        date_retour_prevu__lt=date.today()
    ).count()

    total_membres = Utilisateur.objects.filter(
        is_active=True,
        role=Role.Membre
    ).count()

    # Calcul des données des 6 derniers mois
    today = date.today()
    months_data = []
    months_labels = []
    
    for i in range(5, -1, -1):  # Derniers 6 mois
        month_start = today - relativedelta(months=i)
        month_start = month_start.replace(day=1)
        month_end = month_start + relativedelta(months=1) - relativedelta(days=1)
        
        # Compter les réservations
        reservations_count = Reservation.objects.filter(
            date_reservation__range=[month_start, month_end]
        ).count()
        
        # Compter les emprunts
        emprunts_count = Emprunt.objects.filter(
            date_emprunt__range=[month_start, month_end]
        ).count()
        
        months_labels.append(month_start.strftime('%b'))
        months_data.append({
            'mois': month_start.strftime('%b'),
            'reservations': reservations_count,
            'emprunts': emprunts_count,
            'max': max(reservations_count, emprunts_count) if max(reservations_count, emprunts_count) > 0 else 1
        })

    # Données pour le donut chart réservations
    reservations_confirmees = Reservation.objects.filter(
        statut=ReservationStatus.CONFIRMEE
    ).count()
    reservations_annulees = Reservation.objects.filter(
        statut=ReservationStatus.ANNULEE
    ).count()
    total_reservations = reservations_confirmees + reservations_en_attente + reservations_annulees
    if total_reservations == 0:
        total_reservations = 1

    context = {
        'reservations_en_attente': reservations_en_attente,
        'emprunts_en_cours': emprunts_en_cours,
        'retards': retards,
        'total_membres': total_membres,
        'date': now(),
        'months_data': months_data,
        'reservations_confirmees': reservations_confirmees,
        'reservations_annulees': reservations_annulees,
        'total_reservations': total_reservations
    }

    return render(
        request,
        'utilisateurs/secretaire.html',
        context
    )

def index(request):
    return render(request , 'utilisateurs/index.html')



@login_required
def mon_profil(request : HttpRequest):
    return render(request , 'utilisateurs/mon_profil.html')


@login_required
def edit_profil(request):
    if request.method == "POST":
        user = request.user
        
        user.last_name = request.POST.get("nom")
        user.first_name = request.POST.get("prenom")        
        user.email = request.POST.get("email")
        user.telephone = request.POST.get("telephone")
        user.adresse = request.POST.get("adresse")
        user.date_de_naissance = request.POST.get("date_de_naissance")
        if request.FILES.get("photo_profil"):
            user.photo_profil = request.FILES.get("photo_profil")
            
        user.save()
        
        return JsonResponse({"status": "success"})
    
    return JsonResponse({"status": "error" , "message": "Méthode invalide"})   
    



@login_required
def log_out(request: HttpRequest):
    log_activity(request, "LOGOUT", f"Déconnexion de {request.user.username}")
    logout(request)
    return redirect('loginview')

    


@login_required
def changer_mot_de_passe(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        ancien = request.POST.get("old_password")
        nouveau1 = request.POST.get("new_password1")
        nouveau2 = request.POST.get("new_password2")
        
        if not ancien or not nouveau1 or not nouveau2:
            return JsonResponse({"status": "erreur" , "message": "Tous les champs sont obligatoires"})
        
        if nouveau1 != nouveau2:
            return JsonResponse({"status": "erreur" , "message": "Les deux mots de passes ne correspondent pas"})
        
        if not request.user.check_password(ancien):
            return JsonResponse({"status": "erreur" , "message" : "L'ancien mot de passe est incorrect"})
        
        request.user.set_password(nouveau1)
        request.user.save()
        update_session_auth_hash(request , request.user)
        
        return JsonResponse({"status": "success" , })
    
    return JsonResponse({"status" : "erreur" , "message": "Méthode invalide"})

'''
def get_user_sessions(request):
    sessions_data = []
    if request.method == "GET":
        user_sessions = UserSession.objects.filter(user = request.user).order_by('-date_creation')
        
        
        for s in user_sessions:
            sessions_data.append({
                "cle_session" : s.cle_session,
                "ip_adress" : s.ip_adress,
                "user_agent" : s.user_agent,
                "date_creation" : s.date_creation.strftime("%Y-%m-%d %H:%M:%S"),      
            })
            
    return JsonResponse({"status": "success" , "sessions": sessions_data})


def logout_one_session(request ):
    key = request.POST.get("session_key")
    try:
        if key == request.session.session_key:
            return JsonResponse({
                "status": "Erreur",
                "Message" : "Vous ne pouvez pas supprimer votre propre session"
            })
        
        Session.objects.get(session_key = key).delete()
        UserSession.objects.filter(cle_session = key).delete()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status" : "Erreur" , "message" : str(e)
                             })
        
    '''
    
@login_required
@user_passes_test(is_secretaire)
@permission_requise("gestion_membres")
def gestion_membres(request: HttpRequest):
   

    # Récupérer tous les membres actifs
    membres = Utilisateur.objects.filter(role=Role.Membre, is_active=True).order_by('-date_joined')

    # Statistiques générales
    total_membres = membres.count()
    membres_actifs = membres.filter(is_active=True).count()

    # Membres inscrits ce mois
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    membres_recents = membres.filter(date_joined__gte=debut_mois).count()

    # Total emprunts actifs
    total_emprunts_actifs = Emprunt.objects.filter(
        utilisateur__in=membres,
        statut=EmpruntType.EN_COURS,
        date_retour_effectif__isnull=True
    ).count()

    # Enrichir chaque membre avec ses statistiques
    for membre in membres:
        # Emprunts actifs
        membre.emprunts_actifs = Emprunt.objects.filter(
            utilisateur=membre,
            statut=EmpruntType.EN_COURS,
            date_retour_effectif__isnull=True
        ).count()

        # Retards
        membre.retards = Emprunt.objects.filter(
            utilisateur=membre,
            statut=EmpruntType.EN_COURS,
            date_retour_effectif__isnull=True,
            date_retour_prevu__lt=timezone.now().date()
        ).count()

        # Total emprunts (tous)
        membre.total_emprunts = Emprunt.objects.filter(utilisateur=membre).count()

        # Livres rendus (emprunts terminés)
        membre.livres_rendus = Emprunt.objects.filter(
            utilisateur=membre,
            date_retour_effectif__isnull=False
        ).count()

        # Historique récent (derniers 10 emprunts)
        membre.historique_emprunts = list(Emprunt.objects.filter(
            utilisateur=membre
        ).select_related('livre').order_by('-date_emprunt')[:10])

        # Valeurs par défaut pour éviter les erreurs de template
        if not hasattr(membre, 'emprunts_actifs'):
            membre.emprunts_actifs = 0
        if not hasattr(membre, 'retards'):
            membre.retards = 0
        if not hasattr(membre, 'total_emprunts'):
            membre.total_emprunts = 0
        if not hasattr(membre, 'livres_rendus'):
            membre.livres_rendus = 0
        if not hasattr(membre, 'historique_emprunts'):
            membre.historique_emprunts = []

    context = {
        'membres': membres,
        'total_membres': total_membres,
        'membres_actifs': membres_actifs,
        'membres_recents': membres_recents,
        'total_emprunts_actifs': total_emprunts_actifs,
    }

    return render(request, 'utilisateurs/gestion_membres.html', context)

    
from .forms import SecretaireCreationForm

@login_required
def profil_secretaire(request):
    user = request.user

    if request.method == "POST":
        form = SecretaireCreationForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil modifié avec succès.")
            return redirect("profil_secretaire")
    else:
        form = SecretaireCreationForm(instance=user)

    return render(request, "utilisateurs/profil_secretaire.html", {
        "form": form
    })
    
    
@login_required
@user_passes_test(is_super_administrateur)
def liste_membres_admin(request):
    if request.user.role != Role.SuperAdministrateur:
        messages.error(request , "Vous n'êtes pas autorisés à accéder à cette page")
        return redirect('redirect_to_super_administrateur')
    
    query = request.GET.get('q', '')

    membres = Utilisateur.objects.filter(role=Role.Membre)

    
    if query:
        membres = membres.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    membres = membres.order_by('-date_joined')

    
    paginator = Paginator(membres, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'total_membres': membres.count()
    }

    return render(request, 'utilisateurs/liste_membres_admin.html', context)
    
    

@login_required
@user_passes_test(is_super_administrateur)
def liste_secretaires_admin(request):
    query = request.GET.get('q', '')

    secretaires = Utilisateur.objects.filter(role=Role.Secretaire)

    
    if query:
        secretaires = secretaires.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    
    secretaires = secretaires.order_by('-date_joined')

    
    paginator = Paginator(secretaires, 8)  # mwens pase membres (pi realis)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'total_secretaires': secretaires.count()
    }

    return render(request, 'utilisateurs/liste_secretaires_admin.html', context)

@login_required
@user_passes_test(is_super_administrateur)
def ajouter_utilisateur_admin(request):
    

        if request.method == 'POST':
            form = AdminUserCreationForm(request.POST, request.FILES)

            if form.is_valid():
                user = form.save(commit=False)

                # 🔐 logique metier
                if user.role == Role.Membre:
                    user.numero_membre = generer_numero_membre()

                user.save()

                messages.success(request, "Utilisateur ajouté avec succès")
                return redirect('liste_membres_admin')

            else:
                messages.error(request, "Veuillez corriger les erreurs")

        else:
            form = AdminUserCreationForm()

        
        return render(request, 'utilisateurs/ajouter_utilisateur.html' , {'form': form})

@login_required
@user_passes_test(is_super_administrateur)
def gestion_livres_admin(request):
    livres = Livre.objects.all()
    return render(request, 'utilisateurs/livres.html', {"livres": livres})


from datetime import datetime

@login_required
@user_passes_test(is_super_administrateur)
def logs_systeme_admin(request):

    logs = ActivityLog.objects.select_related('user').order_by('-created_at')
    username = Utilisateur.objects.all()

    role       = request.GET.get('role', '')
    action     = request.GET.get('action', '')
    date_start = request.GET.get('date_start', '')
    date_end   = request.GET.get('date_end', '')
    user_query = request.GET.get('user', '')

    
    if date_start and date_end:
        try:
            d_start = datetime.strptime(date_start, "%Y-%m-%d")
            d_end   = datetime.strptime(date_end, "%Y-%m-%d")

            if d_start > d_end:
                messages.error(request, "Date début pa dwe pi gran pase date fin.")
                return redirect('logs_systeme_admin')

        except ValueError:
            messages.error(request, "Format dat pa valab.")
            return redirect('logs_systeme_admin')

    # ── Filtres ──
    if role:
        logs = logs.filter(user__role=role)
    if action:
        logs = logs.filter(action=action)
    if date_start:
        logs = logs.filter(created_at__date__gte=date_start)
    if date_end:
        logs = logs.filter(created_at__date__lte=date_end)
    if user_query:
        logs = logs.filter(user__username__icontains=user_query)
    # ── Statistiques globales ─────────────────────────────
    stats = {
        'total_connexions':   ActivityLog.objects.filter(action='LOGIN').count(),
        'total_emprunts':     ActivityLog.objects.filter(action='EMPRUNT').count(),
        'total_reservations': ActivityLog.objects.filter(action='RESERVATION').count(),
        'total_suppressions': ActivityLog.objects.filter(action='DELETE').count(),
    }

    # ── Paginasyon — 25 pa paj ────────────────────────────
    paginator = Paginator(logs, 25)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'utilisateurs/logs.html', {
        'page_obj': page_obj,
        'stats':    stats,
        'actions':  ActivityLog.ACTION_CHOICES,
    })    



@login_required
@user_passes_test(is_super_administrateur)
def gestion_permissions(request):
    
     users = Utilisateur.objects.filter(role=Role.Secretaire).prefetch_related('permissions')

     permissions = Permission.objects.all()

     if request.method == "POST":
        user_id = request.POST.get("user_id")
        perms_ids = request.POST.getlist("permissions")

        user = Utilisateur.objects.get(id=user_id)

        # sécurité
        if user.role != Role.Secretaire:
            messages.error(request, "Modification non autorisée.")
            return redirect("gestion_permissions")

        user.permissions.set(perms_ids)

        messages.success(request, f"Permissions mises à jour pour {user.username}")
        return redirect("gestion_permissions")

     return render(request, "utilisateurs/permissions.html", {
        "users": users,
        "permissions": permissions
    })

@login_required
@user_passes_test(is_secretaire)
@permission_requise("delete_user")
def supprimer_utilisateur(request , id):
    if not has_permission(request.user , "delete_user"):
        return HttpResponseForbidden("Accès Réfusé")
    
    user = get_object_or_404(Utilisateur , id = id)
    user.delete()
    
    messages.success(request , "Utilisateur supprimé ")
    return redirect('liste_secretaires_admin')    



@login_required
@user_passes_test(is_super_administrateur)
def ajouter_secretaire(request):
    if request.method == "POST":
        form = SecretaireCreationForm(request.POST, request.FILES)
        if form.is_valid():
            secretaire = form.save(commit=False)
            secretaire.role = Role.Secretaire
            secretaire.save()

            ActivityLog.objects.create(
                user=request.user,
                action="CREATE",
                description=f"Ajout secrétaire: {secretaire.username}"
            )

            messages.success(request, f"Secrétaire '{secretaire.get_full_name()}' ajouté avec succès.")
            return redirect("gestion_permissions")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = SecretaireCreationForm()

    return render(request, "utilisateurs/ajouter_secretaire.html", {"form": form})




def securite_compte(request):
    return render(request , 'utilisateurs/securite_compte.html')

@login_required
def profil_membre(request):

    user = request.user

    favoris_count = Favori.objects.filter(utilisateur=user).count()
    emprunts_count = Emprunt.objects.filter(utilisateur=user , statut = EmpruntType.EN_COURS).count()
    dernier_emprunts = Emprunt.objects.filter(utilisateur=user, statut=EmpruntType.EN_COURS).order_by('-date_emprunt')[:5]
    

    if request.method == "POST":
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        return redirect('profil_membre')

    return render(request, 'utilisateurs/profil_membre.html', {
        'user': user,
        'favoris_count': favoris_count,
        'emprunts_count': emprunts_count,
        'dernier_emprunts': dernier_emprunts
    })
    
    
@login_required
@user_passes_test(is_super_administrateur)
def export_logs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="journal_activites.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Utilisateur', 'Rôle', 'Action', 'Description', 'IP'])

    for log in ActivityLog.objects.select_related('user').order_by('-created_at')[:5000]:
        writer.writerow([
            log.created_at.strftime('%d/%m/%Y %H:%M'),
            log.user.username if log.user else 'Système',
            log.user.role     if log.user else '—',
            log.action,
            log.description,
            log.ip_address or '—',
        ])

    return response


@login_required
@user_passes_test(is_super_administrateur)
def voir_membre_admin(request, id):
    membre = get_object_or_404(Utilisateur, id=id, role=Role.Membre)
    emprunts_actifs = Emprunt.objects.filter(
        utilisateur=membre,
        statut=EmpruntType.EN_COURS
    ).count()
    total_emprunts = Emprunt.objects.filter(utilisateur=membre).count()
    retards = Emprunt.objects.filter(
        utilisateur=membre,
        statut=EmpruntType.EN_COURS,
        date_retour_prevu__lt=date.today()
    ).count()
    return JsonResponse({
        "id": membre.id,
        "username": membre.username,
        "email": membre.email,
        "first_name": membre.first_name,
        "last_name": membre.last_name,
        "telephone": membre.telephone,
        "adresse": membre.adresse,
        "date_joined": membre.date_joined.strftime("%d/%m/%Y"),
        "numero_membre": membre.numero_membre or "—",
        "emprunts_actifs": emprunts_actifs,
        "total_emprunts": total_emprunts,
        "retards": retards,
    })


@login_required
@user_passes_test(is_super_administrateur)
def modifier_membre_admin(request, id):
    membre = get_object_or_404(Utilisateur, id=id, role=Role.Membre)
    if request.method == "POST":
        membre.first_name = request.POST.get("first_name", "").strip()
        membre.last_name  = request.POST.get("last_name", "").strip()
        membre.email      = request.POST.get("email", "").strip()
        membre.telephone  = request.POST.get("telephone", "").strip()
        membre.adresse    = request.POST.get("adresse", "").strip()
        membre.save()
        log_activity(request, "UPDATE", f"Membre modifié : {membre.username}")
        messages.success(request, f"Membre '{membre.username}' modifié avec succès.")
    return redirect("liste_membres_admin")


@login_required
@user_passes_test(is_super_administrateur)
def supprimer_membre_admin(request, id):
    membre = get_object_or_404(Utilisateur, id=id, role=Role.Membre)
    if request.method == "POST":
        username = membre.username
        membre.delete()
        log_activity(request, "DELETE", f"Membre supprimé : {username}")
        messages.success(request, f"Membre '{username}' supprimé avec succès.")
    return redirect("liste_membres_admin")


@login_required
@user_passes_test(is_super_administrateur)
def voir_secretaire_admin(request, id):
    secretaire = get_object_or_404(Utilisateur, id=id, role=Role.Secretaire)
    permissions = list(secretaire.permissions.values('code', 'label'))
    return JsonResponse({
        "id": secretaire.id,
        "username": secretaire.username,
        "email": secretaire.email,
        "first_name": secretaire.first_name,
        "last_name": secretaire.last_name,
        "telephone": secretaire.telephone,
        "adresse": secretaire.adresse,
        "date_joined": secretaire.date_joined.strftime("%d/%m/%Y"),
        "last_login": secretaire.last_login.strftime("%d/%m/%Y %H:%M") if secretaire.last_login else "Jamais",
        "is_active": secretaire.is_active,
        "permissions": permissions,
    })


@login_required
@user_passes_test(is_super_administrateur)
def modifier_secretaire_admin(request, id):
    secretaire = get_object_or_404(Utilisateur, id=id, role=Role.Secretaire)
    if request.method == "POST":
        secretaire.first_name = request.POST.get("first_name", "").strip()
        secretaire.last_name  = request.POST.get("last_name", "").strip()
        secretaire.email      = request.POST.get("email", "").strip()
        secretaire.telephone  = request.POST.get("telephone", "").strip()
        secretaire.adresse    = request.POST.get("adresse", "").strip()
        secretaire.save()
        log_activity(request, "UPDATE", f"Secrétaire modifié : {secretaire.username}")
        messages.success(request, f"Secrétaire '{secretaire.username}' modifié avec succès.")
    return redirect("liste_secretaires_admin")

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Utilisateur.objects.get(pk=uid)
    except (TypeError, ValueError, Utilisateur.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        # Email verifye — mete kont an "an attente" pou admin
        user.email_verifie = True
        user.save()

        # Notifye admin/sekretè
        admins = Utilisateur.objects.filter(
            role__in=[Role.SuperAdministrateur, Role.Secretaire]
        )
        for admin in admins:
            send_mail(
                subject="Nouveau membre en attente d'approbation",
                message=f"Le membre '{user.username}' ({user.email}) a vérifié son email et attend votre approbation.\n\nConnectez-vous pour approuver son compte.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                fail_silently=True,
            )

        messages.success(request, "Email vérifié ! Votre compte est en attente d'approbation par un administrateur.")
        return redirect('loginview')
    else:
        messages.error(request, "Lien invalide ou expiré.")
        return redirect('loginview')
    
    
@login_required
@user_passes_test(is_super_administrateur)
def approuver_membre(request, id):
    membre = get_object_or_404(Utilisateur, id=id, role=Role.Membre)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approuver":
            membre.is_approved = True
            membre.is_active = True
            membre.save()

            # Voye email konfirmasyon bay manb lan
            send_mail(
                subject="Votre compte a été approuvé — Bibliothèque Michèle Tardieu",
                message=f"Bonjour {membre.username},\n\nVotre compte a été approuvé ! Vous pouvez maintenant vous connecter et accéder à nos services.\n\n— L'équipe Bibliothèque Michèle Tardieu",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[membre.email],
                fail_silently=False,
            )

            log_activity(request, "UPDATE", f"Membre approuvé : {membre.username}")
            messages.success(request, f"Membre '{membre.username}' approuvé avec succès.")

        elif action == "rejeter":
            username = membre.username
            membre.delete()
            messages.warning(request, f"Membre '{username}' rejeté et supprimé.")

    return redirect('liste_membres_admin')