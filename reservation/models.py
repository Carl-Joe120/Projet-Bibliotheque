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
    date_reservation = models.DateField(auto_now_add=True)
    date_expiration = models.DateField(default=default_date_expiration)
    confirme = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True , null=True)
    statut = models.CharField(max_length= 20 , choices= ReservationStatus.choices , default= ReservationStatus.En_ATTENTE )
    type_reservation = models.CharField(max_length= 30 , choices=[('physique' , 'Physique') , ('en_ligne' , 'En_ligne')] , default='Physique')
    

    def __str__(self):
        return f"Reservation de {self.utilisateur} pour {self.livre}"


    def est_expire(self):
        return date.today() > self.date_expiration

    def generer_qr_code(self , *args , **kwargs):        
            qr_image = qrcode.make(f"Reservation: {self.utilisateur} -> {self.livre} le {self.date_reservation}" )
            canvas = Image.new('RGB' , qr_image.size , 'white')
            canvas.paste(qr_image)
            buffer = BytesIO()
            canvas.save(buffer, 'PNG')
            filename = f"qr_reservation_{self.pk}.png"
            self.qr_code.save(filename, File(buffer), save=False)
            buffer.close()



    def enregistrer(self , *args , **kwargs):
         if not self.qr_code:
              self.generer_qr_code()
         if self.est_expire() and self.statut != ReservationStatus.EXPIREE:
              self.statut = ReservationStatus.EXPIREE
         super().save(*args , **kwargs)
              

        

