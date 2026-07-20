# Historial Interop Service (M4)

Este servicio es responsable de consolidar el historial clínico de los pacientes, 
escuchando eventos como `caso.cerrado` para actualizar el expediente, 
y de proveer interoperabilidad vía FHIR R4 (solo si existe consentimiento explícito LOPDP).

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8009
```

Para correr workers de Celery (que procesan los historiales):
```bash
celery -A config worker -l info
```
