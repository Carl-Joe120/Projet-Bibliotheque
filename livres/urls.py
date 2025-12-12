from django.urls import path
from . import views

urlpatterns = [
    path('importer_livre_français/', views.importer_livre_français, name='importer-liv-francais'),    
    path('livre_empruntes/' , views.livre_empruntes , name = 'livre_empruntes'),
    path('gestion_emprunts/' , views.gestion_emprunts , name='gestion_emprunts'),
    path('gestion_retours/' , views.gestion_retours , name='gestion_retours'),
    path('gestion_retards/' , views.gestion_retards , name='gestion_retards')
]

