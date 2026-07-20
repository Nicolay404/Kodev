# SAMR — Arquitectura de Sistema
## Rama `arch/system-design`

Este es el plan arquitectónico completo del sistema SAMR (Sistema de Atención Médica Remota).

### Cómo usar esta rama

1. **Contexto:** Lee `ARCHITECTURE.md` (mismo contenido en `AGENTS.md` para Antigravity)
2. **Agente:** La rama usa Antigravity IDE — el agente leerá `AGENTS.md` automáticamente en cada sesión
3. **Trabajo:** El arquitecto de software genera la estructura de carpetas, docker-compose.yml, nginx.conf, y los esqueletos de los 12 microservicios siguiendo el orden en `ARCHITECTURE.md` sección 5

### Dependencias de otras ramas

- `data/persistence-db` — Define el schema PostgreSQL de cada servicio (11 bases de datos independientes)
- `logic/core-services` — Define los eventos RabbitMQ y la comunicación entre servicios
- `sec/security-hardening` — Define la configuración de Nginx, JWT RS256 y RBAC
- `ui/frontend-app` — Depende de que el BFF y API Gateway estén listos
- `ux/design-prototypes` — Define lineamientos visuales y accesibilidad

### Orden de trabajo recomendado

1. `docker-compose.yml` + `nginx/samr.conf`
2. `scripts/init-db.sh` + `scripts/init-rabbitmq.sh`
3. `shared/events/{publisher,consumer}.py`
4. `auth-service/` completo
5. **M1:** patient-service, solicitud-service, monitoring-service
6. **M2:** evaluacion-service
7. **M3:** teleconsult-service, emergency-service, cierre-caso-service
8. **M4:** historial-interop-service, audit-service, admin-integracion-service
9. `notification-service/`
10. `frontend/` + `bff/bff-service/`

### Setup local (próximas fases)

```bash
bash scripts/setup.sh
docker compose up -d
```

---

**Última actualización:** $(date)
**Estado:** En construcción (fase: estructura base)

### Backend local — RabbitMQ

Para el vhost raíz de RabbitMQ se usa una ruta AMQP codificada, compatible tanto con Celery como con Pika:

```env
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/%2F
```

### Backend local — Pruebas

Cada microservicio incluye su configuración de pytest. Con el entorno levantado, una suite individual se ejecuta así:

```bash
docker compose exec auth-service python -m pytest -q
```
