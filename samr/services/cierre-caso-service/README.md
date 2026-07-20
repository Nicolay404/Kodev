# Cierre Caso Service (M3)

Se encarga de la finalización operativa de la atención de un paciente, 
asegurando que todos los requisitos de integridad se cumplan (RNF-28) 
y emitiendo el evento `caso.cerrado` para que M4 pueda consolidar el historial.

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8008
```

O usando Gunicorn:
```bash
gunicorn --bind 0.0.0.0:8008 --workers 3 config.wsgi:application
```
