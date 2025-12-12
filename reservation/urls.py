from . import views
from django.urls import path

urlpatterns = [
    path('' , views.afficher_page_reservation , name='afficher_page_reservation'),
    path('trouver_auteur_ou_titre/' , views.trouver_auteur_ou_titre , name='trouver_auteur_ou_titre'),
    path('reserver/<int:id>/' , views.reserver_livre ,name='reserver_livre' ),    
    path('telecharger_recu/<int:id>/' , views.telecharger_recu , name='telecharger_recu'),
    path('mes_reservations/' , views.mes_reservations , name= 'mes_reservations'),
    path('annuler_reservation/<int:id>/' , views.annuler_reservation , name= 'annuler_reservation'),
    path('gestion_reservations/' , views.gestion_reservations , name='gestion_reservations')
    
]
