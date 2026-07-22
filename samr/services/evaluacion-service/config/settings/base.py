import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-evaluacion')
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
    'apps.evaluacion',
    'tasks',
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
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'evaluacion_db'),
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
PATIENT_SERVICE_URL = os.environ.get('PATIENT_SERVICE_URL', 'http://patient-service:8002')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.evaluacion.permissions.JWTAuthentication',
    ],
}

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/%2F')
SERVICE_NAME = 'evaluacion-service'
MVP_DEFAULT_RISK_LEVEL = os.environ.get('MVP_DEFAULT_RISK_LEVEL', 'medio')
MVP_CRITICAL_TERMS = [term.strip().lower() for term in os.environ.get('MVP_CRITICAL_TERMS', '').split(',') if term.strip()]
MVP_HIGH_TERMS = [term.strip().lower() for term in os.environ.get('MVP_HIGH_TERMS', '').split(',') if term.strip()]

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

CELERY_BROKER_URL = RABBITMQ_URL
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_DEFAULT_QUEUE = 'evaluacion-service.celery'
CELERY_TASK_DEFAULT_EXCHANGE = 'evaluacion-service.celery'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'evaluacion-service.celery'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60

# ============================================================================
# RABBITMQ EVENTOS CONFIGURATION
# ============================================================================

RABBITMQ_EXCHANGE = 'samr.events'
RABBITMQ_QUEUE_EVALUACION = 'evaluacion_service_queue'

RABBITMQ_PUBLISH_KEYS = {
    'riesgo.evaluado': 'riesgo.evaluado',
    'recursos.asignados': 'recursos.asignados',
    'vity.escalation_requested': 'vity.escalation_requested',
    'matching.fallido': 'matching.fallido',
    'ai.decision_logged': 'ai.decision_logged',
}

RABBITMQ_CONSUME_KEYS = [
    'solicitud.validada', 'center.validated', 'center.rejected'
]
