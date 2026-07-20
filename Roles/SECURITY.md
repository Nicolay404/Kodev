# SAMR — Seguridad
## Rama `sec/security-hardening`

> JWT RS256 (Zero Trust), configuración del API Gateway (Nginx: WAF, rate limiting, TLS), RBAC, cifrado, e inmutabilidad de auditoría. Para responsabilidades de cada servicio ver `arch/system-design`; para el detalle de tablas ver `data/persistence-db`.

---

# 1. Zero Trust Interno — Principios

1. **Red:** todos los servicios en red Docker privada, sin puertos expuestos salvo Nginx `:443` y el `bff-service` (único punto de entrada del Frontend).
2. **JWT descentralizado (RS256):** cada servicio verifica el token con la clave pública, sin llamar a `auth-service` en cada petición y sin poder *emitir* tokens.
3. **RBAC explícito por vista**, no solo en el login: `permission_classes` específicas (`IsMedicalStaff`, `IsSystemAdmin`, `IsDPDDelegate`, `IsOwnerOrAdmin`) evaluadas en cada petición.
4. **Cifrado en reposo:** Fernet (AES-128 + HMAC-SHA256) para cédula (`patient-service`); clave `FIELD_ENCRYPTION_KEY` solo en variables de entorno, nunca en código ni en la base de datos.
5. **Cifrado en tránsito:** TLS 1.3 en Nginx y entre el Frontend y el BFF; tráfico interno Docker sin TLS (red privada, no expuesta).
6. **Rate limiting + WAF** en Nginx — primera línea de defensa contra fuerza bruta y SQLi, antes de que la petición llegue a Django.
7. **Validación ORM:** Django ORM usa queries parametrizadas por defecto — sin concatenación de SQL en ningún servicio.
8. **Inmutabilidad de auditoría** a nivel de motor (`REVOKE UPDATE, DELETE`), no solo a nivel de aplicación (ver `audit_log` / `audit_reviews` en `data/persistence-db`).
9. **Consentimiento LOPDP:** `patient-service` mantiene `consent_data`, `consent_ai`, `consent_sharing` como campos explícitos; ningún servicio de IA procesa datos sin verificar `consent_ai=True`.
10. **Auditoría DPD restringida:** el endpoint de auditoría (`audit-service`) solo es accesible por el rol `dpd_delegate` — 403 inmediato para cualquier otro rol, sin exponer datos parciales.
11. **Token de servicio interno** (`X-Service-Token`) distinto del JWT de usuario para toda llamada M2M — rotación cada 90 días.

---

# 2. JWT RS256 — Por qué asimétrico y no HS256 compartido

**Qué se evita:** firmar y verificar con el mismo secreto simétrico (`HS256`) copiado en las variables de entorno de los 12 servicios — con eso, *cualquier* servicio comprometido (o cualquier `.env` filtrado) permite forjar tokens válidos para **todo el sistema**.

**Qué se aplica:** firma con clave privada RSA solo en `auth-service` (`RS256`); los demás servicios reciben únicamente la **clave pública** para verificar, nunca para firmar. Un servicio comprometido solo puede *leer* tokens, nunca *emitir* tokens falsos, porque no posee la clave privada.

```python
# settings/base.py — idéntico salvo en auth-service
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ALGORITHM": "RS256",
    "VERIFYING_KEY": open(config("JWT_PUBLIC_KEY_PATH")).read(),
    # SIGNING_KEY solo se define en auth-service/settings/base.py
}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}
```

`djangorestframework-simplejwt` soporta `RS256` de forma nativa cambiando `ALGORITHM` — el cambio no añade complejidad de código, solo mejora la postura de seguridad alineándola con Zero Trust.

**Docker Compose — solo `auth-service` monta la clave privada:**
```yaml
auth-service:
  build: ./services/auth-service
  environment:
    - JWT_PRIVATE_KEY_PATH=/keys/private.pem
  volumes: ["./keys:/keys:ro"]
# resto de servicios: solo public.pem, sin JWT_PRIVATE_KEY_PATH
```

---

# 3. API Gateway — Nginx (WAF, Rate Limiting, TLS, RBAC previo)

```nginx
# nginx/samr.conf
upstream auth_service               { server auth-service:8001; }
upstream patient_service            { server patient-service:8002; }
upstream solicitud_service          { server solicitud-service:8003; }
upstream monitoring_service         { server monitoring-service:8004; }
upstream evaluacion_service         { server evaluacion-service:8005; }
upstream teleconsult_service        { server teleconsult-service:8006; }
upstream emergency_service          { server emergency-service:8007; }
upstream cierre_caso_service        { server cierre-caso-service:8008; }
upstream historial_interop_service  { server historial-interop-service:8009; }
upstream audit_service              { server audit-service:8010; }
upstream admin_integracion_service  { server admin-integracion-service:8011; }
upstream notification_service       { server notification-service:8012; }

server {
    listen 443 ssl;
    ssl_protocols TLSv1.3;
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    # WAF básico — bloquea patrones de inyección antes de llegar a Django
    if ($request_uri ~* "(union|select|insert|drop|delete|--|;|<script)") { return 403; }

    limit_req_zone $binary_remote_addr zone=auth_zone:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api_zone:10m rate=30r/m;
    limit_req_zone $binary_remote_addr zone=iot_zone:10m rate=100r/m;

    # M1 — Solicitud
    location /api/auth/          { limit_req zone=auth_zone burst=3; proxy_pass http://auth_service; }
    location /api/patients/      { limit_req zone=api_zone;  proxy_pass http://patient_service; }
    location /api/solicitud/     { limit_req zone=api_zone;  proxy_pass http://solicitud_service; }
    location /api/monitoring/iot-events { limit_req zone=iot_zone; proxy_pass http://monitoring_service; }
    location /api/monitoring/    { limit_req zone=api_zone;  proxy_pass http://monitoring_service; }

    # M2 — Evaluación y Asignación
    location /api/evaluacion/    { limit_req zone=api_zone;  proxy_pass http://evaluacion_service; }

    # M3 — Atención
    location /api/teleconsult/   { limit_req zone=api_zone;  proxy_pass http://teleconsult_service; }
    location /api/emergencies/   { limit_req zone=api_zone;  proxy_pass http://emergency_service; }
    location /api/cierre-caso/   { limit_req zone=api_zone;  proxy_pass http://cierre_caso_service; }

    # M4 — Integración e Interoperabilidad Clínica
    location /api/historial/     { limit_req zone=api_zone;  proxy_pass http://historial_interop_service; }
    location /api/history/fhir/  { limit_req zone=api_zone;  proxy_pass http://historial_interop_service; }
    location /api/audit/         { limit_req zone=api_zone;  proxy_pass http://audit_service; }
    location /api/admin/         { limit_req zone=api_zone;  proxy_pass http://admin_integracion_service; }

    location /ws/monitoring/  { proxy_pass http://monitoring_service;  proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_read_timeout 86400s; }
    location /ws/teleconsult/ { proxy_pass http://teleconsult_service; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_read_timeout 86400s; }
}
```

**El BFF y el Gateway:** el `bff-service` vive **delante** de Nginx (ver `arch/system-design`, topología). No existe una ruta `/api/bff/` en Nginx — el BFF es quien inicia las llamadas hacia las rutas de arriba, autenticado con el JWT del usuario que propaga. Nginx sigue aplicando el mismo WAF/rate-limiting a ese tráfico, igual que a cualquier otro cliente.

```python
# Verificación del token interno en el servicio receptor
class IsInternalService(BasePermission):
    def has_permission(self, request, view):
        return request.headers.get("X-Service-Token") == settings.INTERNAL_SERVICE_TOKEN
```

---

# 4. Checklist de Hardening por Servicio

- [ ] `permission_classes` explícitas en cada vista (nunca depender solo del default `IsAuthenticated`).
- [ ] Ningún secreto (clave privada JWT, `FIELD_ENCRYPTION_KEY`, `INTERNAL_SERVICE_TOKEN`) en código o en la base de datos — solo variables de entorno.
- [ ] Docker: usuario no-root, multi-stage build, `HEALTHCHECK` incluido.
- [ ] Toda tabla de auditoría/trazabilidad con `REVOKE UPDATE, DELETE` documentado en `scripts/init-db.sh`.
- [ ] `X-Request-ID` propagado en cada petición para trazabilidad entre logs de distintos servicios.
- [ ] Rotación de `X-Service-Token` cada 90 días vía variable de entorno (sin cambios de código).
- [ ] `audit-service` con endpoint `dpd_delegate`-only devolviendo 403 (no 404 ni 200 con datos parciales) ante cualquier otro rol.

---
*Ver también: `arch/system-design` (topología completa), `logic/core-services` (eventos `auth.login_success` / `auth.account_locked` consumidos por auditoría), `data/persistence-db` (`audit_log` + `audit_reviews`).*
