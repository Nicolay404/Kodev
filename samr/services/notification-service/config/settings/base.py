import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-notification')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# Minimal installed apps (No DB)
INSTALLED_APPS = [
    'rest_framework',
    'tasks',
]

MIDDLEWARE = ['middleware.security.RequestSecurityMiddleware']

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {} # No database for this service (uses only Redis/RabbitMQ)

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://samr:samr_password@rabbitmq:5672//')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
JWT_PUBLIC_KEY_PATH = os.environ.get('JWT_PUBLIC_KEY_PATH', '/keys/public.pem')
NOTIFICATION_TTL_SECONDS = int(os.environ.get('NOTIFICATION_TTL_SECONDS', '86400'))
NOTIFICATION_INBOX_LIMIT = int(os.environ.get('NOTIFICATION_INBOX_LIMIT', '100'))

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================
CELERY_BROKER_URL = RABBITMQ_URL
CELERY_RESULT_BACKEND = 'rpc://'
MVP_NOTIFICATION_BACKEND = os.environ.get('MVP_NOTIFICATION_BACKEND', 'log')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_DEFAULT_QUEUE = 'notification-service.celery'
CELERY_TASK_DEFAULT_EXCHANGE = 'notification-service.celery'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'notification-service.celery'

RABBITMQ_EXCHANGE = 'samr.events'
RABBITMQ_QUEUE_NOTIFICATION = 'notification-service.queue'
RABBITMQ_CONSUME_KEYS = [
    'auth.account_locked',
    'auth.password_reset_requested',
    'vitals.critical_detected',
    'vity.escalation_requested',
    'recursos.asignados',
    'center.validated',
    'center.rejected',
    'emergency.created',
    'emergency.dispatched',
    'teleconsult.session_started',
]
