"""
Configuración de Celery para solicitud-service.
Broker: RabbitMQ
"""

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('solicitud_service')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.imports = ('tasks.validate_with_consortium',)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
