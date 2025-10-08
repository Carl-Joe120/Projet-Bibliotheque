from django.conf import settings
from utilisateurs.models import Utilisateur



def get_full_name(self):
        nom_complet = f"{Utilisateur.first_name} {self.last_name}".strip()
        return f"{nom_complet} ({self.role})" if nom_complet else f"{self.username} ({self.role})"