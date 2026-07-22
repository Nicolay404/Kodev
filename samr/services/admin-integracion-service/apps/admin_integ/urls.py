from django.urls import path
from .views import AvailableCentersView, CenterDetailView, CenterListView, CenterRegisterView, DeviceDetailView, DeviceListView, DeviceRegisterView

urlpatterns = [
    path('centers/register/', CenterRegisterView.as_view(), name='center_register'),
    path('centers/available/', AvailableCentersView.as_view(), name='center_available'),
    path('centers/', CenterListView.as_view(), name='center_list'),
    path('centers/<uuid:center_id>/', CenterDetailView.as_view(), name='center_detail'),
    path('devices/register/', DeviceRegisterView.as_view(), name='device_register'),
    path('devices/', DeviceListView.as_view(), name='device_list'),
    path('devices/<uuid:device_id>/', DeviceDetailView.as_view(), name='device_detail'),
]
