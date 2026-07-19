from django.urls import path
from .views import RiesgoView, CentrosDisponiblesView, MatchingView

urlpatterns = [
    path('riesgo/<int:solicitud_id>/', RiesgoView.as_view(), name='riesgo'),
    path('centros-disponibles/', CentrosDisponiblesView.as_view(), name='centros_disponibles'),
    path('matching/<int:evaluacion_id>/', MatchingView.as_view(), name='matching'),
]
