from datetime import datetime
from django.conf import settings


def date_firma(request):
    return {
        "firma": settings.DATE_FIRMA,
        "an_curent": datetime.now().year,
    }