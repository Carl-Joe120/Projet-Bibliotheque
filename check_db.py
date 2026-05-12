#!/usr/bin/env python
"""
Script simple pour vérifier et ajouter des données de test
"""
import sqlite3
import os
from datetime import date, timedelta

# Connexion à la base de données
db_path = r'C:\Users\jbazi\Desktop\Projet_bibliothèque_Michel_Tardieu\db.sqlite3'

if not os.path.exists(db_path):
    print("Base de données non trouvée")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Lister toutes les tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables dans la BD:")
for table in tables:
    print(f"  - {table[0]}")

# Chercher les tables liées aux emprunts
emprunt_tables = [t[0] for t in tables if 'emprunt' in t[0].lower()]
if emprunt_tables:
    table_name = emprunt_tables[0]
    print(f"\nTable d'emprunts trouvée: {table_name}")

    # Compter les emprunts
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Nombre d'emprunts: {count}")

    if count == 0:
        print("Aucun emprunt trouvé. Vérification des utilisateurs et livres...")

        # Chercher table utilisateurs
        user_tables = [t[0] for t in tables if 'utilisateur' in t[0].lower()]
        if user_tables:
            user_table = user_tables[0]
            cursor.execute(f"SELECT id, username FROM {user_table} LIMIT 1")
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                print(f"Utilisateur trouvé: {user[1]} (ID: {user_id})")

                # Chercher table livres
                livre_tables = [t[0] for t in tables if 'livre' in t[0].lower()]
                if livre_tables:
                    livre_table = livre_tables[0]
                    cursor.execute(f"SELECT id, titre FROM {livre_table} LIMIT 3")
                    livres = cursor.fetchall()
                    if livres:
                        print(f"Livres trouvés: {len(livres)}")

                        # Dates pour 2026
                        dates = [
                            date(2026, 1, 15),  # Janvier 2026
                            date(2026, 2, 15),  # Février 2026
                            date(2026, 3, 15),  # Mars 2026
                        ]

                        # Ajouter des emprunts
                        for i, (livre_date, livre_info) in enumerate(zip(dates, livres)):
                            livre_id, livre_titre = livre_info
                            date_retour = livre_date + timedelta(days=14)

                            try:
                                cursor.execute(f"""
                                    INSERT INTO {table_name}
                                    (utilisateur_id, livre_id, date_emprunt, date_retour_prevu, statut)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (user_id, livre_id, livre_date.isoformat(), date_retour.isoformat(), 'en_cours'))
                                print(f"Ajouté emprunt: {livre_titre} - Date: {livre_date}")
                            except Exception as e:
                                print(f"Erreur lors de l'ajout: {e}")

                        conn.commit()
                        print("Données de test ajoutées!")
                    else:
                        print("Aucun livre trouvé.")
                else:
                    print("Table livres non trouvée.")
            else:
                print("Aucun utilisateur trouvé.")
        else:
            print("Table utilisateurs non trouvée.")
    else:
        # Afficher les emprunts existants
        try:
            cursor.execute(f"""
                SELECT id, date_emprunt, statut
                FROM {table_name}
                ORDER BY date_emprunt DESC LIMIT 5
            """)
            emprunts = cursor.fetchall()
            print("Emprunts existants:")
            for emprunt in emprunts:
                emp_id, emp_date, emp_statut = emprunt
                print(f"ID: {emp_id}, Date: {emp_date}, Statut: {emp_statut}")
        except Exception as e:
            print(f"Erreur lors de la lecture: {e}")
else:
    print("Aucune table d'emprunts trouvée.")

conn.close()