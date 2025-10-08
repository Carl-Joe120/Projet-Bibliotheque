from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
# Create your models here.

class Role(models.TextChoices):
    Membre = 'membre' , 'Membre'
    Secretaire = 'secretaire' , 'Secretaire'
    Administrateur = 'administrateur' ,'Administrateur'
    Employe = 'employe', 'Employe'



class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True , verbose_name='Adresse Electronique')
    role = models.CharField(max_length=20 , choices=Role.choices , default=Role.Membre)
    telephone = models.CharField(max_length=20 , blank=True)
    adresse = models.CharField(max_length=50 , blank=True)
    photo_profil = models.ImageField(upload_to='images/' , blank= True)
    numero_membre = models.CharField(max_length=30 , unique=True , blank=False , null=True , verbose_name= "Numero Membre")
    #date_de_naissance = models.DateField(blank=True)


    REQUIRED_FIELDS = ['email' , 'role' ]

        


    def __str__(self):
        return f"{self.photo_profil}{self.username} ({self.role})"
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def get_full_name(self):
        if self.username and self.role:
            return f"{self.username} ({self.role})"
        return f"{self.username} ({self.role})"
 
 
    def generer_numero_membre(self):
        date_du_jour = datetime.now().strftime('%Y%m%d')
        counte = Utilisateur.objects.filter(role = Role.Membre).count()+1
        return f"MEM-{date_du_jour}-{counte: 03d}"
    
    def save(self , *args , **kwargs ):
        if not self.numero_membre and self.role == Role.Membre:
            self.numero_membre = self.generer_numero_membre()
        super().save( *args ,**kwargs)    
            
        