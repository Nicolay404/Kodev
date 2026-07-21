from django.urls import path, include

urlpatterns = [
    path('api/cierre-caso/', include('apps.cierre.urls')),
]
