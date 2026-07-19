# Evaluacion Service (M2)

Módulo de Evaluación y Asignación.
Se encarga de evaluar el riesgo de una solicitud usando IA/RAG, 
encontrar centros disponibles y hacer el matching.

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8005
```

Para correr workers de Celery:
```bash
celery -A config worker -l info
```
