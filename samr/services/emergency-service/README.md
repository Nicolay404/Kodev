# Emergency Service (M3)

Servicio que gestiona exclusivamente las emergencias médicas (RF-14).
Permite crear alertas de emergencia y que un médico o administrador despache una ambulancia.

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8007
```

O usando Gunicorn:
```bash
gunicorn --bind 0.0.0.0:8007 --workers 3 config.wsgi:application
```
