import pytest
from rest_framework.test import APIClient
from apps.auth.models import User
import uuid
import datetime
from django.utils import timezone

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'password': 'testpassword123'
    }

@pytest.fixture
def create_user(user_data):
    return User.objects.create_user(**user_data)
