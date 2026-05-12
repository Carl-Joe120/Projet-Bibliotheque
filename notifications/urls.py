from django.urls import path
from . import views
urlpatterns = [
    path('ajax/compter/' , views.compter_notifications , name= 'compter_notifications'),
    path('ajax/lister/' , views.liste_notifications , name='liste_notifications'),
    path('lire/<int:id>/' , views.marquer_notifications_comme_lues , name= 'marquer_notifications_comme_lues')
]
