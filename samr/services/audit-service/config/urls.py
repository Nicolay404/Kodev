from django.urls import path, include

urlpatterns = [
    path('api/audit/', include('apps.audit.urls')),
]
