# BFF Service (Backend For Frontend)

Este microservicio se sitúa delante del API Gateway (Nginx). Es el único servicio interno al que el Frontend (React SPA) habla directamente.

Su responsabilidad es **agregar datos** (Data Aggregation) provenientes de distintos microservicios para construir respuestas complejas (como la vista del Dashboard) en una sola llamada HTTP, reduciendo la latencia y la carga en el cliente.

## Características
- Implementado en **FastAPI** para manejo concurrente de I/O de red (`asyncio` + `httpx`).
- Valida el JWT (RS256) antes de propagarlo a los servicios internos.
- No cuenta con base de datos propia.

## Ejecución Local
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
