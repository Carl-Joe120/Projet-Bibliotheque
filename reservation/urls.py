from . import views
from django.urls import path

urlpatterns = [
    path('' , views.afficher_page_reservation , name='afficher_page_reservation'),
    path('trouver_auteur_ou_titre/' , views.trouver_auteur_ou_titre , name='trouver_auteur_ou_titre'),
    path('reserver/<int:id>/' , views.reserver_livre ,name='reserver_livre' ),        
    path('mes_reservations/' , views.mes_reservations , name= 'mes_reservations'),
    path('annuler_reservation/<int:id>/' , views.annuler_reservation , name= 'annuler_reservation'),
    path('gestion_reservations/' , views.gestion_reservations , name='gestion_reservations'),
    path('liste_reservations/' , views.liste_reservations , name='liste_reservations'),
    path('reservations/ajax/<int:reservation_id>/', views.reservation_detail_ajax, name="reservation_detail_ajax"),
    path("detail_reservation/<int:id>/", views.detail_reservation , name='detail_reservation'),
    path('reservation/<int:id>/recu/', views.telecharger_recu, name='telecharger_recu'),
    path("r/<uuid:token>/", views.redirect_scan, name="redirect_scan"),
    path("scan/<uuid:token>/" , views.scan_qr , name= 'scan_qr')
    
]
