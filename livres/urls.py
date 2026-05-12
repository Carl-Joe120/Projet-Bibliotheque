from django.urls import path
from . import views



urlpatterns = [
    path('importer_livre_français/', views.importer_livre_français, name='importer-liv-francais'),    
    path('livre_empruntes/' , views.livre_empruntes_membres , name = 'livre_empruntes_membres'),
    path('gestion_emprunts/' , views.gestion_emprunts , name='gestion_emprunts'),         
    path("valider_retrait/<int:id>/", views.valider_retrait, name="valider_retrait"),
    path('retard_membre/' , views.gestion_retards_membre , name = 'gestion_retards_membre'),
    path('nouveautes_livres' , views.voir_nouveaute_livre , name = 'voir_nouveaute_livre'),
    path('gestion_retard/' , views.gestion_retards_par_secretaire , name='gestion_retards_par_secretaire'),
    path('liste_emprunts_en_cours_secretaire/' , views.liste_emprunts_en_cours_secretaire , name = 'liste_emprunts_en_cours_secretaire'),
    path('gestion_retour/' , views.gestion_des_retours , name = 'gestion_des_retours'),    
    path("statistiques_admin/", views.statistiques_admin, name="statistiques_admin"),
    path('liste/', views.liste_livres_secretaire, name='liste_livres_secretaire'),
    path('ajouter/', views.ajouter_livre, name='ajouter_livre'),
    path('modifier/<int:livre_id>/', views.modifier_livre, name='modifier_livre'),
    path('supprimer/<int:livre_id>/', views.supprimer_livre, name='supprimer_livre'),
    path('gestion_livres_admin/' , views.gestion_livres_admin , name = 'gestion_livres_admin'),
    path('historique_membre/' , views.historique_emprunt_membre , name = 'historique_emprunt_membre'),
    path('favoris/' , views.mes_favoris , name = 'mes_favoris'),
    path('favoris/toggle/<int:livre_id>/', views.toggle_favori, name='toggle_favori'),
    path('objectifs_annuels/' , views.objectifs_annuels , name = 'objectifs_annuels') , 
    path('analyse_lecture/' , views.analyse_lecture , name = 'analyse_lecture'),
    path('historique_retours/', views.gestion_des_retours),
    path('marquer_retour/<int:emprunt_id>/', views.marquer_retour, name='marquer_retour'),
    path('rapports/', views.analyse_rapports, name='analyse_rapports'),
    path('rapports/export-csv/', views.export_csv_rapports, name='export_csv_rapports'),
    path('api/chart-emprunts/', views.get_data_chart_emprunts, name='api_chart_emprunts'),
    path('api/chart-categories/', views.get_data_chart_categories, name='api_chart_categories'),
    path('rapports/pdf/', views.generate_pdf_rapport, name='generate_pdf_rapport'),
    

]

