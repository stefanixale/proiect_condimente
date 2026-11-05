from datetime import datetime

from django.conf import settings

from .models import Categorie


def date_firma(request):
    """Trimite datele firmei catre toate template-urile, plus categoriile pentru meniu."""
    return {
        "firma": settings.DATE_FIRMA,
        "an_curent": datetime.now().year,
        # doar categoriile care au cel putin un produs
        "categorii_meniu": Categorie.objects.filter(produse__isnull=False).distinct(),
    }