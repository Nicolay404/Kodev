"""Configuracion Celery de admin-integracion-service."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("admin_integracion_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.imports = ("tasks.validate_center",)
