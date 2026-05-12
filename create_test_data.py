"""
Script pour ajouter des données de test pour les emprunts
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotheque_Project.settings')
django.setup()

from livres.models import Livre, Emprunt, Categorie
from utilisateurs.models import Utilisateur

def create_test_data():
    print("Création des données de test...")

    # Créer des catégories si elles n'existent pas
    cat1, created = Categorie.objects.get_or_create(nom="Fiction")
    cat2, created = Categorie.objects.get_or_create(nom="Technique")
    cat3, created = Categorie.objects.get_or_create(nom="Science")

    print(f"Catégories créées: {cat1.nom}, {cat2.nom}, {cat3.nom}")

    # Créer des livres si ils n'existent pas
    livre1, created = Livre.objects.get_or_create(
        titre="Python pour les débutants",
        auteur="John Doe",
        isbn="1234567890123",
        categorie=cat2,
        defaults={'quantite': 5, 'date_publication': date(2020, 1, 1)}
    )

    livre2, created = Livre.objects.get_or_create(
        titre="Le Petit Prince",
        auteur="Antoine de Saint-Exupéry",
        isbn="1234567890124",
        categorie=cat1,
        defaults={'quantite': 3, 'date_publication': date(1943, 1, 1)}
    )

    livre3, created = Livre.objects.get_or_create(
        titre="Introduction à l'Intelligence Artificielle",
        auteur="Jane Smith",
        isbn="1234567890125",
        categorie=cat3,
        defaults={'quantite': 2, 'date_publication': date(2022, 1, 1)}
    )

    print(f"Livres créés: {livre1.titre}, {livre2.titre}, {livre3.titre}")

    # Créer un utilisateur de test si nécessaire
    try:
        user = Utilisateur.objects.filter(is_superuser=True).first()
        if not user:
            user = Utilisateur.objects.create_user(
                username="testuser",
                email="test@example.com",
                password="testpass123",
                first_name="Test",
                last_name="User"
            )
        print(f"Utilisateur: {user.get_full_name()}")
    except:
        user = Utilisateur.objects.first()
        if user:
            print(f"Utilisateur existant: {user.get_full_name()}")
        else:
            print("Aucun utilisateur trouvé")
            return

    # Créer des emprunts de test avec différentes dates
    today = date.today()

    # Emprunts en 2026
    dates_2026 = [
        today - timedelta(days=30),  # Mars 2026
        today - timedelta(days=20),  # Mars 2026
        today - timedelta(days=10),  # Avril 2026
        today - timedelta(days=5),   # Avril 2026
    ]

    livres = [livre1, livre2, livre3, livre1]

    for i, (emprunt_date, livre) in enumerate(zip(dates_2026, livres)):
        emprunt, created = Emprunt.objects.get_or_create(
            utilisateur=user,
            livre=livre,
            date_emprunt=emprunt_date,
            defaults={
                'date_retour_prevu': emprunt_date + timedelta(days=14),
                'statut': 'en_cours' if i < 2 else 'retourne'
            }
        )
        if created:
            print(f"Emprunt créé: {emprunt} - Date: {emprunt_date}")
        else:
            print(f"Emprunt existait déjà: {emprunt} - Date: {emprunt_date}")

    print("Données de test créées avec succès!")
    print(f"Total emprunts: {Emprunt.objects.count()}")

if __name__ == "__main__":
    create_test_data()