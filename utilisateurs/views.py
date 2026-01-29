from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth import authenticate , login , logout
from django.contrib import messages
from . import forms
from .models import Role , Utilisateur , UserSession
from django.contrib.auth.decorators import login_required , user_passes_test
from django.http import HttpRequest
from livres.models import Livre , Emprunt
from reservation.models import Reservation , ReservationStatus
from django.db.models import Count 
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import date
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.sessions.models import Session
from ipware import get_client_ip 


# Create your views here.


def loginview(request):    
    if request.method == 'POST':
        form = forms.SigninForm(request , data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            utilisateur = authenticate(request , username = username , password = password)
            if utilisateur is not None:                
                    login(request , utilisateur)
                    
                    '''
                    UserSession.objects.create(
                        user = utilisateur,
                        cle_session = request.session.session_key,
                        ip_adress = get_client_ip(request),
                        user_agent = request.META.get('HTTP_USER_AGENT' , 'Inconnu'),
                        date_creation = now()
                        )                       
                       
                       '''
                       
                                      
                    if utilisateur.role == Role.Membre:
                        return redirect('redirect_to_membre')
                    elif utilisateur.role == Role.Secretaire:
                        return redirect('redirect_to_secretaire')
                    elif utilisateur.role == Role.Administrateur:
                        return redirect('/admin/')
                    elif utilisateur.role == Role.Employe:  
                        return redirect('employe_home')
            else:
                messages.add_message(request , messages.ERROR , "Nom d' utilisateur ou mot de passe incorrecte")

        else:
            messages.add_message(request , messages.ERROR , "Nom d' utilisateur ou mot de passe incorrecte")
            
    else:
        form = forms.SigninForm()
    
    return render(request , 'utilisateurs/login.html' , {'form': form})


def signupview(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            firstname = form.cleaned_data.get('first_name')
            lastname = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')            
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            telephone = form.cleaned_data.get('telephone')
            adresse = form.cleaned_data.get('adresse')
            photo_profil = request.FILES.get('photo_profil')

            newUser = Utilisateur.objects.create_user(
                username=username,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=password1,  
                role=Role.Membre,
                telephone=telephone,
                adresse=adresse,
                photo_profil=photo_profil
            )
            
        else:
            messages.add_message(request , messages.ERROR , "Verifier le format de certains champs")
    else:
        form = forms.SignupForm()        

    return render(request , 'utilisateurs/signup.html' , {'form': form})


def is_administrateur(user):
    return user.role == Role.Administrateur

@login_required
@user_passes_test(is_administrateur , login_url='/')
def redirect_to_admin(request):
    return redirect('admin/')


def is_membre(user):
    return user.role == Role.Membre

@login_required
@user_passes_test(is_membre , login_url='/')
def redirect_to_membre(request: HttpRequest):    
    current_user = request.user
    user_loans = Emprunt.objects.filter(utilisateur = current_user).count()
    user_reservations = Reservation.objects.filter(utilisateur = current_user, statut__in=["en_attente" , "confirmee"]).count()
    user_late_loans = Emprunt.objects.filter(utilisateur = current_user , date_retour_effectif__isnull=True, date_retour_prevu__lt=date.today()).count()
 
    pret_par_mois = (Emprunt.objects.filter(utilisateur = current_user).annotate(month =TruncMonth('date_emprunt')).values('month').annotate(count = Count('id')).order_by('month')
    )
    
    categories_les_plus_lues = ( Emprunt.objects.filter(utilisateur = current_user).values('livre__categorie__nom').annotate(count = Count('id')).order_by('-count')[:5]        
    )
    
    context = {
        'user_loans' : user_loans,
        'user_reservations' : user_reservations,
        'user_late_loans' : user_late_loans,
        'pret_par_mois' : list(pret_par_mois),
        'categories_les_plus_lues' : list(categories_les_plus_lues),
        'user': current_user,
        'recommended_books' : []  
    }   
        
    return render(request , 'utilisateurs/membres.html' , context)

def is_secretaire(user):
    return user.role == Role.Secretaire

@login_required
@user_passes_test(is_secretaire , login_url='/')
def redirect_to_secretaire(request: HttpRequest):
    
    total_reservations = Reservation.objects.filter(statut = ReservationStatus.EN_ATTENTE).count()
    reservations_en_attente = Reservation.objects.filter(statut = 'en_attente').count()
    emprunts_en_cours = Emprunt.objects.filter(date_retour_effectif__isnull = True).count()
    retards = Emprunt.objects.filter(date_retour_effectif__isnull = True , date_retour_prevu__lt = date.today()).count()
    total_membres = Utilisateur.objects.filter(is_active = True , role = Role.Membre).count()
    
    
    context = {
        'total_reservations': total_reservations,
        'reservations_en_attente': reservations_en_attente,
        'emprunts_en_cours': emprunts_en_cours,
        'retards': retards,
        'total_membres': total_membres,
        'date': now()
        }
    return render(request , 'utilisateurs/secretaire.html' , context)

def index(request):
    return render(request , 'utilisateurs/index.html')


@login_required
def user_profile_setting(request):
    return render(request , 'utilisateurs/user-profile-settings.html')

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
def log_out(request : HttpRequest):
    logout(request)
    messages.success(request , "Vous avez déconnecté avec succès")
    return redirect('loginview')  

    
@login_required
def securite_compte(request):
    return render(request , 'utilisateurs/securite_compte.html')

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
def gestion_membres(request: HttpRequest):
    if request.user.role != Role.Secretaire:
        messages.error(request , "Vous n'êtes pas autorisé à accéder à cette page")
    
    membres = Utilisateur.objects.filter(role = Role.Membre)
    
    context = {
        'membres' : membres,
        'total_membres' : membres.count(),
        'membres_actifs' : membres.filter(is_active = True).count(), 
        'membres_inactifs' : membres.filter(is_active = False).count()
    }
    
    return render(request , 'utilisateurs/gestion_membres.html')


@login_required
def toggle_status_membre(request , id):
    if request.user. role != Role.Secretaire:
        messages.error(request , "Vous n'êtes pas autorisés à acceder à cette page")
        return redirect('gestion_membres')
    
    membres = get_object_or_404(Utilisateur , id = id , role = Role.Membre)
    membres.is_active = not membres.is_active
    membres.save()
    return redirect('gestion_membres')


@login_required
def profil_secretaire(request: HttpRequest):
    return render (request , 'utilisateurs/profil_secretaire.html')



    
    