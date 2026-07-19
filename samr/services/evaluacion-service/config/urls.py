from django.urls import path, include

urlpatterns = [
    path('api/evaluacion/', include('apps.evaluacion.urls')),
]
