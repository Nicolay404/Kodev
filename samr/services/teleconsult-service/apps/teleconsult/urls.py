from django.urls import path
from .views import TeleconsultCloseView, TeleconsultSessionDetailView, TeleconsultSessionView

urlpatterns = [
    path('', TeleconsultSessionView.as_view(), name='teleconsult_create'),
    path('<uuid:session_id>/', TeleconsultSessionDetailView.as_view(), name='teleconsult_detail'),
    path('<uuid:session_id>/close/', TeleconsultCloseView.as_view(), name='teleconsult_close'),
]
