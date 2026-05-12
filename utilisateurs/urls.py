from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns =[

    path('' , views.loginview , name='loginview'),    
    path('signup/' , views.signupview , name='signupview'),     
    path('redirect_to_membre/' , views.redirect_to_membre , name = 'redirect_to_membre'),
    path('redirect_to_secretaire/' , views.redirect_to_secretaire , name = 'redirect_to_secretaire'),
    path('administrateur/' , views.redirect_to_admin , name='admin'),
    path('index/' , views.index , name='index'),    
    path('mon_profil/' , views.mon_profil , name='mon_profil'),    
    path('log_out/' , views.log_out , name='log_out'),
    path('update_profil/' , views.edit_profil , name='edit_profil'),
    path('gestion_membres/' , views.gestion_membres , name='gestion_membres'),
    path('profil_secretaire' , views.profil_secretaire , name ='profil_secretaire'),
    path('changer_password/' , views.changer_mot_de_passe , name='changer_mot_de_passe'),
    #path('get_user_sessions/' , views.get_user_sessions , name = 'get_user_sessions'),
    #path('logout_one_session/' , views.logout_one_session , name = 'logout_one_session')  
    path("gestion_membres/", views.gestion_membres, name="gestion_membres"),  
    path("profil-secretaire/", views.profil_secretaire, name="profil_secretaire"),
    path('redirect_to_super_administrateur/' , views.redirect_to_super_administrateur , name='redirect_to_super_administrateur'),
    path('liste_membres_admin/' , views.liste_membres_admin , name = 'liste_membres_admin'),
    path('liste_secretaire_admin/' , views.liste_secretaires_admin , name = 'liste_secretaires_admin'),
    path('admin_ajouterutilisateur/' , views.ajouter_utilisateur_admin , name= 'ajouter_utilisateur_admin'),
    path('gestion_livres_admin/' , views.gestion_livres_admin , name = 'gestion_livres_admin'),
    path('admin_logs' , views.logs_systeme_admin , name = 'logs_systeme_admin'), 
    path('gestion_permissions/' , views.gestion_permissions , name = 'gestion_permissions'),
    path('securite_compte/' , views.securite_compte , name = 'securite_compte'), 
    path('ajouter_secretaire/' , views.ajouter_secretaire , name = 'ajouter_secretaire'),
    path('profil_membre/' , views.profil_membre , name = 'profil_membre'),
    path('superadmin/logs/',views.logs_systeme_admin, name='logs_systeme_admin'),
    path('admin/logs/export/', views.export_logs_csv, name='export_logs_csv'),
    path('membres/voir/<int:id>/',  views.voir_membre_admin,  name='voir_membre_admin'),
    path('membres/modifier/<int:id>/',  views.modifier_membre_admin,  name='modifier_membre_admin'),
    path('membres/supprimer/<int:id>/', views.supprimer_membre_admin, name='supprimer_membre_admin'),
    path('secretaires/voir/<int:id>/',     views.voir_secretaire_admin,     name='voir_secretaire_admin'),
    path('secretaires/modifier/<int:id>/', views.modifier_secretaire_admin, name='modifier_secretaire_admin'),

    path('verify-code/', views.verify_code, name='verify_code'),
    path('membres/approuver/<int:id>/', views.approuver_membre, name='approuver_membre'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
    
