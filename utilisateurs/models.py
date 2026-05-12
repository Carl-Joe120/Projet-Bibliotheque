from cProfile import label
from turtle import mode

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
# Create your models here.

class Permission(models.Model):
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)   
    
    def __str__(self):
        return self.label

    @classmethod
    def creer_permissions_defaut(cls):
        PERMISSIONS_DEFAUT = [
            ("delete_user",          "Supprimer utilisateur"),
            ("modifier_utilisateur", "Modifier utilisateur"),
            ("valider_emprunt",      "Valider un emprunt"),
            ("ajouter_livre",        "Ajouter un livre"),
            ("supprimer_livre",      "Supprimer un livre"),
            ("modifier_livre",       "Modifier un livre"),
            ("gestion_membres",      "Gérer les membres"),
            ("gestion_emprunts",     "Gérer les emprunts"),
            ("gestion_reservations", "Gérer les réservations"),
        ]
        for code, label in PERMISSIONS_DEFAUT:
            cls.objects.get_or_create(code=code, defaults={"label": label})       
            

@receiver(post_migrate)
def initialiser_permissions(sender, **kwargs):
    if sender.name == 'utilisateurs':
        Permission.creer_permissions_defaut()

class Role(models.TextChoices):
    Membre = 'membre' , 'Membre'
    Secretaire = 'secretaire' , 'Secretaire'
    Administrateur = 'administrateur' ,'Administrateur'
    SuperAdministrateur = 'super administrateur', 'super administrateur'

def generer_numero_membre():
    date_du_jour = datetime.now().strftime('%Y%m%d')
    from .models import Utilisateur, Role  
    count = Utilisateur.objects.filter(role=Role.Membre).count() + 1
    return f"MEM-{date_du_jour}-{count:03d}"

class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True , verbose_name='Adresse Electronique')
    role = models.CharField(max_length=20 , choices=Role.choices , default=Role.Membre)
    telephone = models.CharField(max_length=20 , blank=True)
    adresse = models.CharField(max_length=50 , blank=True)
    photo_profil = models.ImageField(upload_to='images/' , blank= True)
    numero_membre = models.CharField(max_length=30 , unique=True , blank=True , null=True , default=generer_numero_membre , verbose_name= "Numero Membre")
    date_de_naissance = models.DateField(blank=True , null=True )
    last_nouveaute_seen = models.DateTimeField(blank=True , null = True)
    permissions = models.ManyToManyField(Permission , blank=True)
    email_verified = models.BooleanField(default = False , verbose_name = "Email vérifié")
    is_approved = models.BooleanField(default = False , verbose_name = "Compte approuvé")
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_expiration = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['email' , 'role' ]

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def get_full_name(self):
        if self.username and self.role:
            return f"{self.username} ({self.role})"
        return f"{self.username} ({self.role})"
    
    def nom_complet(self):
         return f"{self.first_name}  {self.last_name}"       
 
     
 


    def save(self , *args , **kwargs ):
        if not self.numero_membre and self.role == Role.Membre:
            self.numero_membre = generer_numero_membre()
        super().save(*args , **kwargs)
            
            
            
class ActivityLog(models.Model):

    ACTION_CHOICES = [
        ("CREATE", "Création"),
        ("UPDATE", "Modification"),
        ("DELETE", "Suppression"),
        ("LOGIN", "Connexion"),
        ("LOGOUT", "Déconnexion"),
        ("EMPRUNT", "Emprunt"),
        ("RESERVATION", "Réservation"),
        ("AUTRE", "Autre"),
        ("RETOUR", "Retour livre"),
        ("ANNULATION" , "Annulation"),
        ("EXPORT" , "Exportation données"),
        ("Autre" , "Autre"),
        
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"            
            
            

        
class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)
    cle_session = models.CharField(max_length=255 )
    ip_adress = models.GenericIPAddressField(null=True , blank=True)
    user_agent = models.TextField(null=True , blank = True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    
    
    