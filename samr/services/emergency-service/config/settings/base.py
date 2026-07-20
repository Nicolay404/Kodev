import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-emergency')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.emergency',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'middleware.security.RequestSecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'emergency_db'),
        'USER': 'samr',
        'PASSWORD': os.environ.get('DB_PASSWORD', 'samr_postgres_password'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JWT_PUBLIC_KEY_PATH = os.environ.get('JWT_PUBLIC_KEY_PATH', '/keys/public.pem')
SERVICE_TOKEN = os.environ.get('SERVICE_TOKEN', 'samr-internal-service-token-default')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.emergency.permissions.JWTAuthentication',
    ],
}

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/%2F')
SERVICE_NAME = 'emergency-service'
MVP_FIRST_AID_GUIDE = os.environ.get('MVP_FIRST_AID_GUIDE', 'Mantenga la calma y contacte al servicio de emergencias. Siga únicamente las indicaciones del personal autorizado.')

RABBITMQ_EXCHANGE = 'samr.events'
RABBITMQ_PUBLISH_KEYS = {
    'emergency.dispatched': 'emergency.dispatched',
}
RABBITMQ_CONSUME_KEYS = []
