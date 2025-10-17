from . import views
from django.urls import path

urlpatterns = [
    path('' , views.reserver_livre , name='reserver_livre'),
    path('' , views.trouver_auteur_ou_titre , name='trouver_auteur_ou_titre')
]
