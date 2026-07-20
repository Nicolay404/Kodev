from django.urls import path
from .views import HistorialView, FHIRHistoryView

urlpatterns = [
    path('historial/<int:patient_id>/', HistorialView.as_view(), name='historial_get'),
    path('history/fhir/<int:patient_id>/', FHIRHistoryView.as_view(), name='fhir_history'),
]
