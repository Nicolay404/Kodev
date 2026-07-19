from django.urls import path, include

urlpatterns = [
    path('api/solicitud/', include('apps.solicitud.urls')),
]
