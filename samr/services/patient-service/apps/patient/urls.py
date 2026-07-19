from django.urls import path
from .views import PatientMeView, PatientSummaryView

urlpatterns = [
    path('me/', PatientMeView.as_view(), name='patient_me'),
    path('<int:pk>/summary/', PatientSummaryView.as_view(), name='patient_summary'),
]
