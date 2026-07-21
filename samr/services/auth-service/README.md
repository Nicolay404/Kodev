# Auth Service

Servicio transversal para la gestión de identidad y autenticación.
Emite tokens JWT (RS256).

## Instalación Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Generación de llaves

```bash
python scripts/generate_keys.py
```

## Ejecución

```bash
python manage.py migrate
python manage.py runserver 8001
```
