from django.urls import path
from .views import RiesgoView, CentrosDisponiblesView, MatchingView, MisCasosView

urlpatterns = [
    path('riesgo/<uuid:solicitud_id>/', RiesgoView.as_view(), name='riesgo'),
    path('centros-disponibles/', CentrosDisponiblesView.as_view(), name='centros_disponibles'),
    path('mis-casos/', MisCasosView.as_view(), name='evaluacion_mis_casos'),
    path('matching/<uuid:evaluacion_id>/', MatchingView.as_view(), name='matching'),
]
