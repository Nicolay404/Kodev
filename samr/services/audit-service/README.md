# Audit Service (M4)

Módulo de auditoría inmutable. 
Registra de forma *append-only* las decisiones tomadas por modelos de IA (RF-18) mediante la escucha de eventos (ej. `riesgo.evaluado`), 
y proporciona un acceso controlado para revisión por parte del Delegado de Protección de Datos (DPD) (RF-20).

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8010
```

Para correr workers de Celery (que ingieren los logs de auditoría asíncronamente):
```bash
celery -A config worker -l info
```
