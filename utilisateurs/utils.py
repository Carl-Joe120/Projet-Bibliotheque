from functools import wraps
from django.contrib import messages
from django.conf import settings
from utilisateurs.models import Utilisateur , ActivityLog
from ipware import get_client_ip
from django.http import HttpResponseForbidden
from django.shortcuts import redirect 


def get_full_name(self):
    nom_complet = f"{self.first_name} {self.last_name}".strip()
    return f"{nom_complet} ({self.role})" if nom_complet else f"{self.username} ({self.role})"



def log_activity(request=None, action="", description="", user=None, ip=None):
    if request:
        ip, _ = get_client_ip(request)
        user = request.user if request.user.is_authenticated else None

    ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip
    )    
    
def has_permission(user, code):
    return user.permissions.filter(code=code).exists()


def permission_requise(code):
    def decorateur(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not has_permission(request.user, code):
                messages.error(request , "Accès refusé : vous n'avez pas la permission requise pour effectuer cette action.")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorateur