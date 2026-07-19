from django.urls import path
from .views import RegisterView, LoginView, RefreshTokenView, MeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]
