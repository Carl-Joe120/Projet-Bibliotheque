from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse

from .models import Reservation, ReservationStatus
from .utils import generer_pdf_qr
from notifications.models import Notifications, NotificationsType


@receiver(post_save, sender=Reservation)
def confirmation_reservation_automatique(sender, instance, created, **kwargs):

    if created:

        # 1 - PDF QR
        pdf_buffer = generer_pdf_qr(instance)

        # 2 - EMAIL
        email = EmailMessage(
            subject="Réservation reçue",
            body=(
                f"Bonjour {instance.utilisateur.nom_complet()},\n\n"
                "Votre réservation est enregistrée et en attente de validation.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.utilisateur.email]
        )

        email.attach(
            f"reservation_{instance.id}.pdf",
            pdf_buffer.getvalue(),
            "application/pdf"
        )

        email.send(fail_silently=True)

        # 3 - NOTIFICATION (REMISE)
        Notifications.objects.create(
            utilisateur=instance.utilisateur,
            titre="Réservation envoyée",
            message=f"Votre réservation du livre {instance.livre.titre} est en attente de validation.",
            link=reverse("detail_reservation", kwargs={"id": instance.id}),
            type_notifications=NotificationsType.DISPONIBILITE
        )