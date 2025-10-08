from django.db import models
from django.conf import settings
from datetime import datetime
# Create your models here.



class NotificationsType(models.TextChoices):
    RETARD = 'retard' , "RETARD DE RETOUR"
    DISPONIBILITE = 'disponibilite' , "LIVRE DISPONIBLE"
    NOUVEAUTE = 'nouveaute' , "UN NOUVEAU LIVRE AJOUTÉ"



class Notifications(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank= True)
    lu = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(default=datetime.now)
    type_notifications = models.CharField(max_length= 25 ,choices= NotificationsType.choices , default=NotificationsType.DISPONIBILITE)

    def __str__(self):
        return f"{self.titre} - {'lu'if self.lu else 'non lu '}"