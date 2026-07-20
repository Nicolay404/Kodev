from django.urls import path
from .views import CierreCasoView, VerificarCasoView

urlpatterns = [
    path('<int:caso_id>/close/', CierreCasoView.as_view(), name='cierre_close'),
    path('<int:caso_id>/verify/', VerificarCasoView.as_view(), name='cierre_verify'),
]
