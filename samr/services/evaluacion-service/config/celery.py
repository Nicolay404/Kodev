"""
Configuración de Celery para evaluacion-service.
Broker: RabbitMQ
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
app = Celery('evaluacion_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.imports = ('tasks.procesar_solicitud',)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
