from django.contrib import admin
from notifications.models import Notifications
# Register your models here.

@admin.register(Notifications) 
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur' , 'titre' , 'message' , 'lu' , 'date_envoi')
    list_filter = ['utilisateur']
    search_fields = ['utilisateur']
