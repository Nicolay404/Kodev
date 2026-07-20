from django.urls import path, include

urlpatterns = [
    path('api/admin/', include('apps.admin_integ.urls')),
]
