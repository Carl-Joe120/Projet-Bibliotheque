from django.shortcuts import render , redirect
from django.contrib.auth import authenticate , login , logout
from django.contrib import messages
from . import forms
from .models import Role , Utilisateur
from django.contrib.auth.decorators import login_required , user_passes_test
from django.http import HttpRequest
from livres.models import Livre , Emprunt
from reservation.models import Reservation
from django.db.models import Count 
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import date

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
                    if utilisateur.role == Role.Membre:
                        return redirect('redirect_to_membre')
                    elif utilisateur.role == Role.Secretaire:
                        return redirect('secretaire_home')
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



@login_required
def secretaire(request):
    return render(request , 'utilisateurs/secretaire.html')


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
    return render(request , 'utilisateurs/membres.html' , {'user': current_user})



def index(request):
    return render(request , 'utilisateurs/index.html')


@login_required
def user_profile_setting(request):
    return render(request , 'utilisateurs/user-profile-settings.html')

@login_required
def user_profile(request):
    return render(request , 'utilisateurs/pages-profile.html')

@login_required
def user_activite(request):
    return render(request , 'utilisateurs/user-activities.html')

@login_required
def log_out(request : HttpRequest):
    logout(request)
    messages.success(request , "Vous avez déconnecté avec succès")
    return redirect('loginview')

    
    

def dashboard_membre(request : HttpRequest):
    user_loans = Emprunt.objects.filter(utilisateur = request.user).count()
    user_reservation = Reservation.objects.filter(utilisateur = request.user).count()
    user_late_loans = Livre.objects.filter(Utilisateur = request.user , date_retour_effectif__isnull = True , date_retour_prevu__lt = date.today())
 
    pret_par_mois = (Emprunt.objects.filter(utilisateur =request.user).annotate(month =TruncMonth('date_emprunt')).values('month').annotate(count = Count('id')).order_by('month')
    )
    
    categories_les_plus_lues = ( Emprunt.objects.filter(utilisateur=request.user).values('livre__categorie__nom').annotate(count = Count('id')).order_by('-count')[:5]        
    )
    
    context = {
        'user_loans' : list(user_loans),
        'user_reservation' : list(user_reservation),
        'user_late_loans' : list(user_late_loans),
        'pret_par_mois' : list(pret_par_mois),
        'categories_les_plus_lues' : list(categories_les_plus_lues),
        
    }
    
    return render(request , 'utilisateurs/membres.html' , context)
    