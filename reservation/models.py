from django.db import models
from django.conf import settings
from livres.models import Livre
from datetime import date,timedelta
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image


# Create your models here.

class ReservationStatus(models.TextChoices):
    EN_ATTENTE = 'en_attente', "En_ATTENTE"
    CONFIRMEE = 'confirmee' , "CONFIRMEE"
    ANNULEE = 'annulee' , "ANNULEE"
    EXPIREE = 'expiree' , "EXPIREE"
    TRANSFORMEE = 'transforme_en_emprunt', "Tranformee en emprunt"


def default_date_expiration():
    return date.today() + timedelta(days=3)



class Reservation(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre , on_delete=models.CASCADE)
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField(default=default_date_expiration)    
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True , null=True)
    statut = models.CharField(max_length= 50 , choices= ReservationStatus.choices , default= ReservationStatus.EN_ATTENTE)
    type_reservation = models.CharField(max_length= 30 , choices=[('physique' , 'Physique') , ('en_ligne' , 'En_ligne')] , default='physique')    
    message_utilisateur = models.TextField(blank=True , null= True)
    date_confirmation = models.DateField(blank=True , null= True)
    
    

    def est_expire(self):
        return date.today() > self.date_expiration

           
    def __str__(self):
        return f"Reservation de {self.utilisateur} pour {self.livre}"
    

