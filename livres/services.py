from datetime import date
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse

from notifications.models import Notifications, NotificationsType
from .models import Emprunt


def verifier_retards_et_envoyer_notifications():

    emprunts_retard = Emprunt.objects.select_related(
        "utilisateur",
        "livre"
    ).filter(
        date_retour_effectif__isnull=True,
        date_retour_prevu__lt=date.today(),
        email_retard_envoye=False
    )

    for emprunt in emprunts_retard:

        utilisateur = emprunt.utilisateur
        livre = emprunt.livre

        # Notification App
        if not emprunt.notification_retard_envoye:

            Notifications.objects.create(
                utilisateur=utilisateur,
                titre="Livre en retard",
                message=(
                    f"Vous avez un retard sur le livre "
                    f"<< {livre.titre} >>. "
                    f"La date prévue était le {emprunt.date_retour_prevu}."
                ),
                link=reverse("gestion_retards_membre"),
                type_notifications=NotificationsType.RETARD
            )

            emprunt.notification_retard_envoye = True

        # Email
        email = EmailMessage(
            subject="Livre en retard",
            body=(
                f"Bonjour {utilisateur.nom_complet()},\n\n"
                f"Vous avez un retard sur le livre "
                f"<< {livre.titre} >>.\n"
                f"La date de retour prévue était le "
                f"{emprunt.date_retour_prevu}.\n\n"
                "Merci de le rapporter dès que possible."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[utilisateur.email]
        )

        email.send(fail_silently=True)

        emprunt.email_retard_envoye = True
        emprunt.save(update_fields=[
            "email_retard_envoye",
            "notification_retard_envoye"
        ])
