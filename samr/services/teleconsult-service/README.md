# Teleconsult Service (M3)

Servicio que gestiona las sesiones de teleconsulta, ofreciendo endpoints para crear 
la sesión médica y un WebRTC signalling server mediante WebSockets (Django Channels y Redis).

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8006
```

Nota: Daphne se usa como servidor ASGI en el contenedor Docker.
```bash
daphne -b 0.0.0.0 -p 8006 config.asgi:application
```
