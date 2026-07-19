from django.urls import path
from .views import TeleconsultSessionView

urlpatterns = [
    path('', TeleconsultSessionView.as_view(), name='teleconsult_create'),
]
