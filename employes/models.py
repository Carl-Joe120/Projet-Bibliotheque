from django.db import models

# Create your models here.
class Employe(models.Model):
    ROLE_CHOICES = [
        ('BIBLIOTHECAIRE','Bibliothecaire'),
        ('ASSISTANT','Assistant'),
        ('AGENT_SECURITE','Agent de securite'),
        
    ]
    nom_complet = models.CharField(max_length=100)
    role = models.CharField(max_length=30 , choices=ROLE_CHOICES)
    date_embauche = models.DateField()
    salaire_mensuel = models.DecimalField(max_digits=6 , decimal_places=2)
    actif = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='images/' , null= True)
    
    def __str__(self):
        return f"{self.nom_complet} - {self.role}"
    
    