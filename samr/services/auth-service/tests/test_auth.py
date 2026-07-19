import pytest
from django.urls import reverse
from rest_framework import status
from apps.auth.models import User, LoginAttempt

@pytest.mark.django_db
class TestAuthAPI:
    
    def test_register(self, api_client):
        url = reverse('register')
        data = {'email': 'newuser@example.com', 'password': 'securepassword'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'email' in response.data
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_login(self, api_client, create_user, user_data):
        url = reverse('login')
        response = api_client.post(url, user_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        
        # Verify attempt was logged
        assert LoginAttempt.objects.filter(user=create_user, success=True).exists()

    def test_refresh_token(self, api_client, create_user, user_data):
        # 1. Login to get token
        login_url = reverse('login')
        login_response = api_client.post(login_url, user_data, format='json')
        refresh_token = login_response.data['refresh_token']
        
        # 2. Refresh token
        refresh_url = reverse('token_refresh')
        response = api_client.post(refresh_url, {'refresh_token': refresh_token}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data

    def test_me(self, api_client, create_user, user_data):
        # 1. Login
        login_response = api_client.post(reverse('login'), user_data, format='json')
        access_token = login_response.data['access_token']
        
        # 2. Get profile
        url = reverse('me')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user_data['email']

    def test_login_blocked(self, api_client, create_user, user_data):
        url = reverse('login')
        wrong_data = {'email': user_data['email'], 'password': 'wrongpassword'}
        
        # 5 failed attempts
        for _ in range(5):
            response = api_client.post(url, wrong_data, format='json')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
        # 6th attempt, even with correct password, should be blocked
        response = api_client.post(url, user_data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.data['error'] == 'Cuenta bloqueada temporalmente'
