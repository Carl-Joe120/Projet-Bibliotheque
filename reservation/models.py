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
    En_ATTENTE = 'en_attente', "En_ATTENTE"
    CONFIRMEE = 'confirmee' , "CONFIRMEE"
    ANNULEE = 'annulee' , "ANNULEE"
    EXPIREE = 'expiree' , "EXPIREE"


def default_date_expiration():
    return date.today() + timedelta(days=3)



class Reservation(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre , on_delete=models.CASCADE)
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField(default=default_date_expiration)
    confirme = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True , null=True)
    statut = models.CharField(max_length= 20 , choices= ReservationStatus.choices , default= ReservationStatus.En_ATTENTE )
    type_reservation = models.CharField(max_length= 30 , choices=[('physique' , 'Physique') , ('en_ligne' , 'En_ligne')] , default='Physique')
    livre_demande = models.CharField(max_length= 255 , blank=True , null= True)
    message_utilisateur = models.TextField(blank=True , null= True)
    date_confirmation = models.DateField(blank=True , null= True)

    def est_expire(self):
        return date.today() > self.date_expiration

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if not self.qr_code:
            qr_data = f"Reservation ID: {self.id}\nUtiliateur: {self.utilisateur.username}\nLivre: {self.livre.titre}\nDate: {self.date_reservation}\nExpiration: {self.date_expiration}"
            qr_image = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_image.save(buffer , format='PNG')
            filename = f'Reservation_{self.id}.png'
            self.qr_code.save(filename , File(buffer) , save = False)
            super().save(*args , **kwargs)

    def __str__(self):
        return f"Reservation de {self.utilisateur} pour {self.livre}"
    

