from django.contrib import admin
from reservation.models import Reservation

# Register your models here.


@admin.register(Reservation)
class AdminReservation(admin.ModelAdmin):
    list_display = ('utilisateur','livre' , 'date_reservation' , 'date_expiration' , 'confirme' , 'qr_code')
    list_filter = ['utilisateur']
    search_fields = ['livre']
    list_per_page = 5