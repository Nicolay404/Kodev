# Monitoring Service (M1)

Servicio encargado de la ingesta de datos IoT de dispositivos de monitoreo,
detección de anomalías en signos vitales, y notificaciones WebSocket en tiempo real.

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8004
```

Nota: Requiere Redis para WebSocket layer (Daphne).
