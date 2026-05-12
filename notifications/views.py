from django.shortcuts import render , get_object_or_404 , redirect
from django.contrib.auth.decorators import login_required
from .models import Notifications
from django.http import JsonResponse 
# Create your views here.


'''

montre notifikasyon itilizatè

'''
@login_required
def compter_notifications(request):
    valeur_notif = Notifications.objects.filter(utilisateur = request.user , lu = False).count()
    return JsonResponse({'valeur_notif' : valeur_notif})

@login_required
def liste_notifications(request):
    notifications = Notifications.objects.filter(utilisateur = request.user).order_by('-date_envoi')[:5]
    
    data = []
    for n in notifications:
        data.append({
            'id' : n.id,
            'titre' : n.titre,
            'message' : n.message , 
            'link' : n.link,
            'lu' : n.lu,
            'date_envoi' : n.date_envoi.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return JsonResponse({'data' : data})

def marquer_notifications_comme_lues(request, id):
    notif = get_object_or_404(
        Notifications,
        utilisateur=request.user,
        id=id
    )

    notif.lu = True
    notif.save(update_fields=['lu'])

    return redirect(notif.link)