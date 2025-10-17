from django.contrib import messages
from django.shortcuts import redirect
from .utils import importer_livres
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest


from django.shortcuts import render
from .models import Livre

def importer_livre_français(request):
    total_imported, google_used = importer_livres()
    messages.success(request, f"{total_imported} livres importés avec succès.")
    if google_used > 0:
        messages.info(request, f"{google_used} livres ont été complétés avec Google Books API.")
    return redirect('list_livres')



def liste_livres(request):
    livres = Livre.objects.all().order_by("-date_publication")
    return render(request, "livres/liste_livre.html", {"livres": livres})


@login_required
def livre_empruntes(request):
    return render(request , 'livres/livres_empruntes.html')