# Solicitud Service

Servicio del módulo M1 encargado de interactuar con el paciente y registrar solicitudes.

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8003
```

Para correr workers de Celery:
```bash
celery -A tasks worker -l info
```
