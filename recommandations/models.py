from django.db import models
from utilisateurs.models import Utilisateur
from livres.models import Livre
from django.conf import settings
from datetime import datetime


# Create your models here.


class HistoriqueConsultation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur , on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre , on_delete=models.CASCADE)
    date_consultation = models.DateTimeField(default= datetime.now)


    def __str__(self):
        return f"{self.utilisateur} a consulté {self.livre} le {self.date_consultation.strftime('%d/%m/%y')}"