import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-admin')
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
    'apps.admin_integ',
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
        'NAME': os.environ.get('DB_NAME', 'admin_db'),
        'USER': os.environ.get('DB_USER', 'samr'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'samr_postgres_password'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'options': '-c search_path=public'
        },
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
        'apps.admin_integ.permissions.DualAuthentication',
    ],
}

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/%2F')
SERVICE_NAME = 'admin-integracion-service'
MVP_CENTER_VALIDATION_OUTCOME = os.environ.get('MVP_CENTER_VALIDATION_OUTCOME', 'validated')

CELERY_BROKER_URL = RABBITMQ_URL
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_DEFAULT_QUEUE = 'admin-integracion-service.celery'
CELERY_TASK_DEFAULT_EXCHANGE = 'admin-integracion-service.celery'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'admin-integracion-service.celery'
CELERY_TASK_ACKS_LATE = True

RABBITMQ_EXCHANGE = 'samr.events'
RABBITMQ_PUBLISH_KEYS = {
    'center.registered': 'center.registered',
    'device.registered': 'device.registered',
}
RABBITMQ_CONSUME_KEYS = []
