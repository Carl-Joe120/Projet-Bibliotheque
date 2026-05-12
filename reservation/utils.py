from django.conf import settings
from django.urls import reverse
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader



def generer_pdf_qr(reservation):
    buffer = BytesIO()

    # 🔥 PRAN IP LOCAL OTOMATIK
    base_url = settings.SITE_URL

    qr_path = reverse("redirect_scan", args=[reservation.qr_token])
    qr_url = f"{base_url}{qr_path}"

    qr = qrcode.make(qr_url)
    qr_image = ImageReader(qr.get_image())

    pdf = canvas.Canvas(buffer)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 760, "Reservation confirmée")
    pdf.drawString(100, 740, f"Livre : {reservation.livre.titre}")
    pdf.drawString(100, 720, f"Membre : {reservation.utilisateur.nom_complet()}")
    pdf.drawString(100, 700, f"Numéro réservation : {reservation.id}")
    pdf.drawImage(qr_image, 100, 430, width=200, height=200)
    pdf.drawString(100, 400, "Présentez ce QR code à la bibliothèque")
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer    