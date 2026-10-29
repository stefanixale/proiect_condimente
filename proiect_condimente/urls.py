from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("aplicatie_condimente/", include("aplicatie_condimente.urls")),
]