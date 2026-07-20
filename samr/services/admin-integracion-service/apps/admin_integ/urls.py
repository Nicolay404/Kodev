from django.urls import path
from .views import CenterRegisterView, AvailableCentersView, DeviceRegisterView

urlpatterns = [
    path('centers/register/', CenterRegisterView.as_view(), name='center_register'),
    path('centers/available/', AvailableCentersView.as_view(), name='center_available'),
    path('devices/register/', DeviceRegisterView.as_view(), name='device_register'),
]
