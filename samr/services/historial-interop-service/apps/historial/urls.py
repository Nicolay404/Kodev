from django.urls import path
from .views import HistorialView, FHIRHistoryView

urlpatterns = [
    path('historial/<uuid:patient_id>/', HistorialView.as_view(), name='historial_get'),
    path('history/fhir/<uuid:patient_id>/', FHIRHistoryView.as_view(), name='fhir_history'),
]
