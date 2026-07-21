from django.urls import path, include

urlpatterns = [
    path('api/teleconsult/', include('apps.teleconsult.urls')),
]
