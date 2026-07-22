import asyncio
import os
import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SAMR BFF", version="1.0")
BFF_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "BFF_ALLOWED_ORIGINS", "http://localhost:5173"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=BFF_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "X-Request-ID"],
)
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL", "https://nginx")
JWT_PUBLIC_KEY_PATH = os.environ.get("JWT_PUBLIC_KEY_PATH", "/keys/public.pem")
VERIFY_GATEWAY_TLS = os.environ.get("VERIFY_GATEWAY_TLS", "true").lower() == "true"
http_client = None


@app.on_event("startup")
async def startup():
    global http_client
    http_client = httpx.AsyncClient(base_url=API_GATEWAY_URL, verify=VERIFY_GATEWAY_TLS, timeout=5.0)


@app.on_event("shutdown")
async def shutdown():
    if http_client: await http_client.aclose()


def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401, "Token no provisto")
    token = authorization[7:]
    try:
        with open(JWT_PUBLIC_KEY_PATH, "rb") as key_file: key = serialization.load_pem_public_key(key_file.read())
        payload = jwt.decode(
            token, key, algorithms=["RS256"], issuer="samr-auth-service"
        )
        if payload.get("type") != "access": raise ValueError("Tipo inválido")
        return {"token": token, "payload": payload}
    except (OSError, jwt.InvalidTokenError, ValueError) as exc: raise HTTPException(401, "Token inválido") from exc


@app.get("/health")
async def health(): return {"status": "ok"}


@app.get("/dashboard/")
async def dashboard(credentials: dict = Depends(verify_token)):
    role = credentials["payload"].get("rol")
    endpoints_by_role = {
        "patient": {
            "patient": "/api/patients/me/",
            "solicitudes": "/api/solicitud/",
            "monitoring": "/api/monitoring/alerts/",
            "atencion": "/api/cierre-caso/mis-casos/",
            "emergencias": "/api/emergencies/",
            "teleconsultas": "/api/teleconsult/",
            "notificaciones": "/api/notifications/",
        },
        "professional": {
            "evaluacion": "/api/evaluacion/mis-casos/",
            "monitoring": "/api/monitoring/alerts/",
            "atencion": "/api/cierre-caso/mis-casos/",
            "emergencias": "/api/emergencies/",
            "teleconsultas": "/api/teleconsult/",
            "notificaciones": "/api/notifications/",
        },
        "nurse": {
            "monitoring": "/api/monitoring/alerts/",
            "emergencias": "/api/emergencies/",
            "notificaciones": "/api/notifications/",
        },
        "center_admin": {
            "evaluacion": "/api/evaluacion/mis-casos/",
            "monitoring": "/api/monitoring/alerts/",
            "atencion": "/api/cierre-caso/mis-casos/",
            "emergencias": "/api/emergencies/",
            "teleconsultas": "/api/teleconsult/",
            "notificaciones": "/api/notifications/",
        },
        "system_admin": {
            "centros": "/api/admin/centers/",
            "dispositivos": "/api/admin/devices/",
            "faq": "/api/solicitud/faq/",
            "notificaciones": "/api/notifications/",
        },
        "dpd_delegate": {
            "auditoria": "/api/audit/decisions/",
            "notificaciones": "/api/notifications/",
        },
    }
    endpoints = endpoints_by_role.get(role)
    if endpoints is None:
        raise HTTPException(403, "Rol no soportado")
    token = credentials["token"]
    async def fetch(name, path):
        try:
            response = await http_client.get(path, headers={"Authorization": f"Bearer {token}"})
            return name, response.json() if response.status_code == 200 else {"error": response.status_code}
        except httpx.HTTPError: return name, {"error": "service_unavailable"}
    return {"role": role, **dict(await asyncio.gather(*(fetch(name, path) for name, path in endpoints.items())))}
