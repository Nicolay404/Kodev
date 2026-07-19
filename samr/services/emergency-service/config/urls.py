from django.urls import path, include

urlpatterns = [
    path('api/emergencies/', include('apps.emergency.urls')),
]
