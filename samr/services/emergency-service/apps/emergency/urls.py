from django.urls import path
from .views import EmergencyListView, EmergencyDispatchView

urlpatterns = [
    path('', EmergencyListView.as_view(), name='emergency_list'),
    path('<int:emergency_id>/dispatch/', EmergencyDispatchView.as_view(), name='emergency_dispatch'),
]
