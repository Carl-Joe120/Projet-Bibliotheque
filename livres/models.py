from turtle import mode

from django.db import models
from django.conf import settings
from datetime import timedelta,date

import utilisateurs
# Create your models here.

class Categorie(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"

class Tags(models.Model):
    nom = models.CharField(max_length= 30)

class Livre(models.Model):
    titre = models.CharField(max_length=500)
    auteur = models.CharField(max_length=500)
    isbn = models.CharField(max_length=50 , unique=True)
    resume = models.TextField(blank= True)
    date_publication = models.DateField()
    categorie = models.ForeignKey(Categorie , on_delete=models.SET_NULL , null=True)
    tags = models.ManyToManyField(Tags , blank= True)    
    couverture = models.ImageField(upload_to='couvertures/', blank=True , null=True)    
    quantite = models.PositiveIntegerField(default=1)
    date_ajout_livre = models.DateField(auto_now_add=True)
    est_nouveau = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titre} - {self.auteur}"

def default_retour_prevu():
    return date.today() + timedelta(days=14)

class EmpruntType(models.TextChoices):
    EN_COURS = 'en_cours' , "EN COURS"
    RETOURNE = 'retourne' , "RETOURNE"
    

class Emprunt(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)
    date_emprunt = models.DateField(auto_now_add=True)
    date_retour_prevu = models.DateField(default=default_retour_prevu)
    statut = models.CharField(max_length= 30 , choices= EmpruntType.choices , default= EmpruntType.EN_COURS)
    date_retour_effectif = models.DateField(blank=True , null=True)
    livre = models.ForeignKey(Livre , on_delete=models.CASCADE , null=True) 
    valide_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL , blank=True , null=True , related_name='validateur_emprunt')
    email_retard_envoye = models.BooleanField(default=False)
    notification_retard_envoye = models.BooleanField(default=False)


    def en_retard(self):
        return self.date_retour_effectif is None and date.today() > self.date_retour_prevu
    
    def __str__(self):
        return f"{self.utilisateur} -> {self.livre}"
    

class Favori(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre , on_delete=models.CASCADE)


class ObjectifLecture(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete= models.CASCADE)
    objectif = models.IntegerField(default=10)
    anne = models.IntegerField()

