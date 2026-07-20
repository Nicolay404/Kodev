# Notification Service (Transversal)

Servicio puramente reactivo encargado de enviar notificaciones push a los clientes (móviles, web) mediante FCM o WebSockets (delegados).
Escucha eventos críticos en RabbitMQ (`solicitud.validada`, `emergency.dispatched`, `atencion.iniciada`) y notifica.
No expone endpoints HTTP a Nginx y no posee base de datos propia.

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Para correr workers de Celery (que ingieren los eventos):
```bash
celery -A config worker -l info
```
