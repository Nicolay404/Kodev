import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-notification')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# Minimal installed apps (No DB)
INSTALLED_APPS = [
    'tasks',
]

MIDDLEWARE = []

ROOT_URLCONF = ''

DATABASES = {} # No database for this service (uses only Redis/RabbitMQ)

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://samr:samr_password@rabbitmq:5672//')

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================
CELERY_BROKER_URL = RABBITMQ_URL
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

RABBITMQ_EXCHANGE = 'samr.events'
RABBITMQ_QUEUE_NOTIFICATION = 'notification_service_queue'
RABBITMQ_CONSUME_KEYS = [
    'solicitud.validada',
    'emergency.dispatched',
    'atencion.iniciada',
]
