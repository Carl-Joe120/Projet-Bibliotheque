from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from .models import Reservation , ReservationStatus
from datetime import date
import qrcode
from io import BytesIO
from django.core.files import File


@receiver(post_save , sender= Reservation)
def generer_code_qr_reservation(sender , instance , created , **kwargs):
    if instance.type_reservation == 'en_ligne':
        return
    
    if instance.statut != ReservationStatus.CONFIRMEE:
        return
    
    if instance.qr_code:
        return
    
    qr_data = (
        f"Reservation ID: {instance.id}\n"
        f"Utilisateur : {instance.utilisateur}\n"
        f"Livre : {instance.livre.titre}\n"
        f"Date confirmation : {instance.date_confirmation}\n"
        f"Statut : {instance.statut}\n"
    )
    
    qr_image = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_image.save(buffer , format='PNG')
    buffer.seek(0)
    
    filename = f"reservation_{instance.id}.png"
    instance.qr_code.save(filename , File(buffer) , save=False)
    