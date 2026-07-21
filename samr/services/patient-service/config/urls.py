from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/patients/', include('apps.patient.urls')),
]
