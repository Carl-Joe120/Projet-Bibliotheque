from .models import Notifications

def notifications_nav(request):
    if not request.user.is_authenticated:
        return {}

    
    qs = Notifications.objects.filter(
        utilisateur=request.user
    ).order_by('-date_envoi')

    
    unread_count = qs.filter(lu=False).count()

    
    notifications_nav = qs[:5]

    return {
        'notifications_nav': notifications_nav,
        'notifications_unread_count': unread_count
    }
