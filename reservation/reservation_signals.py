from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reservation , ReservationStatus
import qrcode
from django.utils import timezone
from django.conf import settings
from .utils import generer_pdf_qr
from notifications.models import Notifications , NotificationsType
from django.core.mail import EmailMessage
from django.urls import reverse


@receiver(post_save , sender = Reservation)
def confirmation_reservation_automatique(sender , instance , **kwargs):
    
    if instance.statut == ReservationStatus.EN_ATTENTE:
        
        instance.statut = ReservationStatus.CONFIRMEE
        instance.date_confirmation = timezone.now()
        instance.save(update_fields=["date_confirmation"])
        
        pdf_buffer = generer_pdf_qr(instance)
        
        
        Notifications.objects.create(utilisateur = instance.utilisateur, 
                                     titre = "Réservation confirmée" , message = f"Votre réservation du livre << {instance.livre.titre} >> est confirmée." , 
                                     link = reverse("detail_reservation" , kwargs={"id" : instance.id}), 
                                     type_notifications = NotificationsType.DISPONIBILITE )
        
        email = EmailMessage(
            subject="Réservation confirmée - QR Code",
            body=(
                f"Bonjour {instance.utilisateur.nom_complet()},\n\n"
                f"Votre réservation du livre << {instance.livre.titre} >> est confirmée.\n"
                "Veuillez présenter le QR code ci-joint lors du retrait.\n\n"
                "Merci"
                
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
        
        
        
        