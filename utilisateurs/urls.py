from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns =[

    path('' , views.loginview , name='loginview'),    
    path('signup/' , views.signupview , name='signup'),     
    path('redirect_to_membre/' , views.redirect_to_membre , name = 'redirect_to_membre'),
    path('redirect_to_secretaire/' , views.redirect_to_secretaire , name = 'redirect_to_secretaire'),
    path('administrateur/' , views.redirect_to_admin , name='admin'),
    path('index/' , views.index , name='index'),
    path('securite/' , views.securite_compte , name = 'securite_compte'),
    path('mon_profil/' , views.mon_profil , name='mon_profil'),    
    path('log_out/' , views.log_out , name='log_out'),
    path('update_profil/' , views.edit_profil , name='edit_profil'),
    path('gestion_membres/' , views.gestion_membres , name='gestion_membres'),
    path('profil_secretaire' , views.profil_secretaire , name ='profil_secretaire'),
    path('changer_password/' , views.changer_mot_de_passe , name='changer_mot_de_passe')
    #path('get_user_sessions/' , views.get_user_sessions , name = 'get_user_sessions'),
    #path('logout_one_session/' , views.logout_one_session , name = 'logout_one_session')    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
    
