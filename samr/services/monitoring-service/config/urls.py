from django.urls import path, include

urlpatterns = [
    path('api/monitoring/', include('apps.monitoring.urls')),
]
