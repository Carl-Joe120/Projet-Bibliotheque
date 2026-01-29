from io import BytesIO
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def generer_pdf_qr(reservation):
    buffer = BytesIO()

   
    qr = qrcode.make(
        f"RESERVATION-{reservation.id}\n"
        f"LIVRE: {reservation.livre.titre}\n"
        f"DATE: {reservation.date_confirmation.strftime('%d/%m/%Y')}"
    )

    
    qr_pil_image = qr.get_image()   # ← OBLIGATOIRE
    qr_reader = ImageReader(qr_pil_image)

   
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, "Réservation confirmée")
    pdf.drawString(100, 720, f"Livre : {reservation.livre.titre}")  
    pdf.drawString(100, 700, f"Membre : {reservation.utilisateur.nom_complet()}")

 
    pdf.drawImage(qr_reader, 100, 450, width=200, height=200)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer
