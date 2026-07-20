import os
import jwt
import httpx
import asyncio
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

app = FastAPI(title="BFF Service - SAMR")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL", "http://nginx")
JWT_PUBLIC_KEY_PATH = os.environ.get("JWT_PUBLIC_KEY_PATH", "/keys/public.pem")

# Global variables to reuse HTTP client
http_client = httpx.AsyncClient(verify=False) # Internal verification only

@app.on_event("startup")
async def startup_event():
    global http_client
    http_client = httpx.AsyncClient(verify=False)

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no provisto o inválido")
    
    token = authorization.split(" ")[1]
    
    try:
        with open(JWT_PUBLIC_KEY_PATH, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload, token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/dashboard/")
async def get_dashboard(auth_data: tuple = Depends(verify_token)):
    payload, token = auth_data
    headers = {"Authorization": f"Bearer {token}"}
    
    # Agregar llamadas simultáneas a los microservicios a través del Gateway
    patient_id = payload.get("usuario_id") # Por simplicidad asumimos que es el del token
    rol = payload.get("rol")
    
    # URL de los endpoints internos a agregar
    urls = {}
    if rol == 'patient':
        urls = {
            "profile": f"{API_GATEWAY_URL}/api/patients/me/",
            "alerts": f"{API_GATEWAY_URL}/api/monitoring/alerts/",
        }
    else:
        urls = {
            "emergencies": f"{API_GATEWAY_URL}/api/emergencies/",
            "alerts": f"{API_GATEWAY_URL}/api/monitoring/alerts/",
        }
    
    async def fetch(key, url):
        try:
            response = await http_client.get(url, headers=headers)
            if response.status_code == 200:
                return key, response.json()
            return key, {"error": response.status_code}
        except Exception as e:
            return key, {"error": str(e)}

    # Ejecutar peticiones en paralelo
    tasks = [fetch(key, url) for key, url in urls.items()]
    results = await asyncio.gather(*tasks)
    
    dashboard_data = {key: data for key, data in results}
    return JSONResponse(content=dashboard_data)
