from django.urls import path
from .views import CierreCasoView, MisCasosView, VerificarCasoView

urlpatterns = [
    path('mis-casos/', MisCasosView.as_view(), name='mis_casos'),
    path('<uuid:caso_id>/close/', CierreCasoView.as_view(), name='cierre_close'),
    path('<uuid:caso_id>/verify/', VerificarCasoView.as_view(), name='cierre_verify'),
]
