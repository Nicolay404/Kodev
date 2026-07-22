from django.urls import path
from .views import EmergencyDetailView, EmergencyDispatchView, EmergencyListView

urlpatterns = [
    path('', EmergencyListView.as_view(), name='emergency_list'),
    path('<uuid:emergency_id>/', EmergencyDetailView.as_view(), name='emergency_detail'),
    path('<uuid:emergency_id>/dispatch/', EmergencyDispatchView.as_view(), name='emergency_dispatch'),
]
