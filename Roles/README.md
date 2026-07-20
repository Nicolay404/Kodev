# SAMR — Sistema de Atención Médica Remota

> **Arquitectura:** Microservicios orientada a eventos (EDA) · v4.0.0
> **Base:** ESP-HS-SAMR v1.0.5 (4 módulos) · Diagrama de Clases (Apéndice A) · `requisitosfuncionaes_nofuncionales.xlsx` (20 RF · 38 RNF)
> **Stack:** Django 5.0 · DRF · Channels · Celery · RabbitMQ 3.13 · Redis 7.2 · PostgreSQL 16 (Supabase) · React 18.3 · TypeScript 5.5 · Docker Compose

Este repositorio organiza el trabajo por rama según la responsabilidad de cada parte del sistema. Esta rama (`main`) es el punto de entrada: no contiene el detalle técnico de cada capa, solo el mapa para encontrarlo.

## Los 4 módulos de negocio

| Módulo | Caso de uso | RF que agrupa | Servicios que lo implementan |
|---|---|---|---|
| **M1 — Módulo de Solicitud** | CU-001 | RF-01 a RF-07 | `patient-service`, `solicitud-service`, `monitoring-service` |
| **M2 — Módulo de Evaluación y Asignación** | CU-002 | RF-08 a RF-12 | `evaluacion-service` |
| **M3 — Módulo de Atención** | CU-003 | RF-13 a RF-15 | `teleconsult-service`, `emergency-service`, `cierre-caso-service` |
| **M4 — Módulo de Integración e Interoperabilidad Clínica** | CU-004 | RF-16 a RF-20 | `historial-interop-service`, `audit-service`, `admin-integracion-service` |

Servicios transversales (no ligados a un solo módulo): `auth-service`, `notification-service`, `bff-service`.

## Topología general

```
Frontend (React) → BFF → API Gateway (Nginx) → 12 microservicios de negocio
                                              ↕
                                   RabbitMQ (Event Bus) + Redis (cache/WS)
```

El BFF vive **entre el Frontend y el API Gateway** (no detrás de él): agrega respuestas de varios servicios para el dashboard y es quien llama al Gateway, nunca al revés.

## Dónde está cada cosa (ramas)

| Rama | Qué contiene | Archivo principal |
|---|---|---|
| [`arch/system-design`](../../tree/arch/system-design) | Patrones arquitectónicos, topología completa, límites de cada microservicio por módulo, estructura de carpetas, `docker-compose.yml`, reglas para generación de código | `ARCHITECTURE.md` |
| [`data/persistence-db`](../../tree/data/persistence-db) | Los 11 schemas PostgreSQL (uno por servicio con BD propia), tablas, convenciones de índices y claves, script `init-db.sh` | `DATABASE.md` |
| [`logic/core-services`](../../tree/logic/core-services) | Event Bus RabbitMQ (exchange `samr.events`, DLX), catálogo completo de eventos de dominio, WebSocket (Channels), llamadas M2M, configuración Celery | `CORE_SERVICES.md` |
| [`sec/security-hardening`](../../tree/sec/security-hardening) | JWT RS256 (Zero Trust), configuración Nginx (WAF, rate limiting, TLS), RBAC, cifrado en reposo/tránsito, inmutabilidad de auditoría | `SECURITY.md` |
| [`ui/frontend-app`](../../tree/ui/frontend-app) | Stack React/TypeScript, gestión de estado (Zustand), resiliencia del cliente, WebRTC | `FRONTEND.md` |
| [`ux/design-prototypes`](../../tree/ux/design-prototypes) | Accesibilidad WCAG 2.1 AA, jerarquía visual de urgencia, sistema de diseño | `UX.md` |

## Los 13 microservicios de un vistazo

| # | Servicio | Puerto | Módulo | Base de datos |
|---|---|---|---|---|
| 1 | `auth-service` | 8001 | Transversal | `auth_db` |
| 2 | `patient-service` | 8002 | M1 | `patient_db` |
| 3 | `solicitud-service` | 8003 | M1 | `solicitud_db` |
| 4 | `monitoring-service` | 8004 | M1 | `monitoring_db` + Redis |
| 5 | `evaluacion-service` | 8005 | M2 | `evaluacion_db` |
| 6 | `teleconsult-service` | 8006 | M3 | `teleconsult_db` + Redis |
| 7 | `emergency-service` | 8007 | M3 | `emergency_db` |
| 8 | `cierre-caso-service` | 8008 | M3 | `cierre_db` |
| 9 | `historial-interop-service` | 8009 | M4 | `historial_db` |
| 10 | `audit-service` | 8010 | M4 | `audit_db` (append-only) |
| 11 | `admin-integracion-service` | 8011 | M4 | `admin_db` |
| 12 | `notification-service` | 8012 | Transversal | Redis únicamente |
| 13 | `bff-service` | 8000 | Transversal (edge, delante del Gateway) | Ninguna |

---
*Índice generado a partir de `ARQUITECTURA_MAESTRA_SAMR_v4.md` — para el detalle completo de cada capa, entra a la rama correspondiente de la tabla de arriba.*
