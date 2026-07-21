# Admin Integración Service (M4)

Este servicio centraliza la administración del sistema y su integración:
- Registro de Centros Médicos y validación de consorcio (RF-19).
- Exponer catálogo de centros disponibles (leído por `evaluacion-service` en M2) (RF-10).
- Registro de Dispositivos IoT (RF-19).

Provee un entorno de seguridad donde solo los usuarios con el rol `system_admin` pueden registrar entidades,
pero permite el consumo de solo-lectura entre servicios vía `X-Service-Token`.

## Ejecución Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8011
```
