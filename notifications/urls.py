from django.urls import path
from . import views
urlpatterns = [
    path('ajax/compter/' , views.compter_notifications , name= 'compter_notifications'),
    path('ajax/lister/' , views.liste_notifications , name='liste_notifications')
]
