from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("info", views.info, name="info"),
    path("log", views.log, name="log"),
    path("despre", views.despre, name="despre"),
    path("istoric", views.istoric, name="istoric"),

    path("produse", views.produse, name="produse"),
    path("produs/<int:id_produs>", views.produs, name="produs"),
    path("categorii/<str:nume>", views.categorie, name="categorie"),

    path("contact", views.contact, name="contact"),
    path("cos_virtual", views.cos_virtual, name="cos_virtual"),
    path("retete", views.retete, name="retete"),
    path("blog", views.blog, name="blog"),
    re_path(r"^accesare(?P<id_accesare>[0-9]+)$", views.accesare_detalii, name="accesare_detalii"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)