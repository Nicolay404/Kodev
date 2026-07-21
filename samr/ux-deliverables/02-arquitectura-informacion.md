# 02 — Arquitectura de la Información
## SAMR — Sistema de Atención Médica Remota

> SAMR es multi-rol con permisos estrictos (RBAC): `patient`, `professional`, `nurse` (paramédico), `center_admin`, `system_admin`, `dpd_delegate` — confirmados exactos contra `auth-service` (ver [00](00-alineacion-backend.md) §0.1). La IA no es un sitemap único — **es un sitemap por rol** que comparte un shell de navegación común. Este documento define ambos niveles.
>
> **v1.1**: este sitemap fue auditado contra los endpoints reales de los 13 microservicios. Se marcan tres niveles de soporte: ✅ **soportado** (el endpoint existe y hace lo que la pantalla necesita), 🟡 **soportado parcialmente** (existe pero con limitaciones que cambian el diseño), 🔴 **pendiente de backend** (no hay ningún endpoint — la pantalla se conserva como especificación lista para cuando exista, pero no debe implementarse contra un backend simulado). Cada marca referencia su entrada en el doc [00](00-alineacion-backend.md).

---

## 2.1 Sitemap completo

```
/ (público, sin autenticación)
├── /login                                                                          ✅
├── /registro                                                                       ✅ (siempre crea rol "patient" — §0.2)
├── /recuperar-contrasena                                                           🔴 G11 — sin endpoint en auth-service
│   ├── /recuperar-contrasena/verificar
│   └── /recuperar-contrasena/nueva
│
└── /app  (autenticado — shell con Navbar + Sidebar según rol)
    │
    ├── /app/dashboard                                                              🟡 G8 — BFF no diferencia por rol
    │
    ├── ── PACIENTE / FAMILIAR ──────────────────────────────────
    │   ├── /app/solicitudes/nueva            (chat de orientación + formulario)     ✅ POST /chat/, POST /
    │   ├── /app/solicitudes/:id              (solo inmediatamente tras crearla)      🟡 G2 — sin GET, no persiste tras recargar
    │   ├── /app/emergencias                  (mis emergencias reportadas)            ✅ GET /api/emergencies/ (auto-filtrado por patient_id)
    │   ├── /app/emergencias/:id              (guía primeros auxilios + estado)       ✅
    │   ├── /app/teleconsultas/:id            (sala — solo si ya tengo el room_token) 🟡 G3/G4 — no hay forma de descubrirlo vía API
    │   ├── /app/historial                    (mi expediente clínico consolidado)     ✅ GET /historial/<patient_id>/
    │   └── /app/ayuda                        (bot de preguntas frecuentes)           ✅ GET /faq/
    │
    ├── ── PROFESIONAL DE SALUD / EVALUADOR CLÍNICO ────────────
    │   ├── /app/casos                        (cola global, no personal)              🟡 §0.3 M2 — sin filtro por profesional
    │   ├── /app/casos/:id                    (evaluación de riesgo, inmutable)       ✅ GET /riesgo/<solicitud_id>/
    │   ├── /app/casos/:id/matching           (1 acción, sin elegir centro)           🟡 G5 — auto-asignación, sin lista de candidatos
    │   ├── /app/teleconsultas/:id            (crear sesión + sala WebRTC)            🟡 G3 — crear funciona, no hay agenda/lista ni cierre
    │   ├── /app/emergencias                  (ver todas — rol clínico)               ✅
    │   ├── /app/emergencias/:id              (despachar)                             ✅ POST .../dispatch/
    │   ├── /app/casos/:id/cierre             (solo si viene de emergencia)           🟡 G3/G9 — cierre exclusivo de casos con `emergency_id`
    │   └── /app/pacientes/:id/historial      (lectura — cualquier paciente)          🟡 G10 — sin chequeo de relación de cuidado
    │
    ├── ── ENFERMERO / PARAMÉDICO ───────────────────────────────
    │   ├── /app/emergencias                 (cola de emergencias, rol incluido)      ✅
    │   ├── /app/emergencias/:id              (despachar)                             ✅
    │   └── /app/pacientes/:id/historial      (solo lectura — NO puede escribir)      🟡 G12 — sin endpoint de escritura
    │
    ├── ── ADMINISTRADOR DE CENTRO MÉDICO ───────────────────────
    │   ├── /app/casos                        (ver — mismo endpoint global)           🟡 §0.3 M2
    │   └── /app/casos/:id/verify             (verificar completitud, no cerrar)      ✅ GET .../verify/ — cerrar NO (G9, solo `professional`)
    │
    ├── ── ADMINISTRADOR SAMR ───────────────────────────────────
    │   ├── /app/admin/centros/nuevo          (registro — formulario)                 ✅ POST /centers/register/
    │   ├── /app/admin/centros/disponibles    (solo los ya validados, sin pendientes) 🟡 G6 — sin listado completo ni detalle
    │   ├── /app/admin/dispositivos/nuevo     (registro y vinculación)                ✅ POST /devices/register/
    │   └── /app/admin/faq                    (gestionar FAQ del bot — NUEVO, §0.4)   ✅ GET/POST/PATCH /api/solicitud/faq/
    │
    ├── ── DELEGADO DE PROTECCIÓN DE DATOS (DPD) ────────────────
    │   └── /app/auditoria                    (lista de 100, filtro solo client-side) 🟡 §0.3 M6 — sin filtros server-side; detalle sale del mismo listado, no hay GET individual
    │
    ├── ── TRANSVERSAL (todo rol autenticado) ───────────────────
    │   ├── /app/notificaciones                                                       🔴 G7 — notification-service sin API
    │   ├── /app/perfil                       (rico solo para rol patient)            🟡 solo `patient-service` tiene perfil extendido; otros roles solo ven email/rol de auth
    │   ├── /app/configuracion
    │   │   ├── /app/configuracion/seguridad  (solo "cerrar sesión" es real)          🔴 G14 — sin cambio de contraseña ni sesiones (JWT stateless)
    │   │   ├── /app/configuracion/privacidad (consentimientos LOPDP — solo patient)  ✅ PATCH /api/patients/me/
    │   │   ├── /app/configuracion/notificaciones                                     🔴 G7
    │   │   └── /app/configuracion/accesibilidad (100% local, sin backend)            ✅
    │
    └── ── SISTEMA / ERROR ───────────────────────────────────────
        ├── /403          (permisos insuficientes)
        ├── /404           (no encontrado)
        ├── /500           (error del servidor)
        ├── /mantenimiento
        └── /offline       (overlay, no ruta navegable — ver doc 11)
```

**Rutas retiradas del sitemap v1.0** (existían en la versión previa, sin ningún endpoint que las respalde — no se listan arriba para no sugerir que están listas para implementarse; quedan documentadas como pendientes en [00](00-alineacion-backend.md)):

| Ruta retirada | Rol | Motivo |
|---|---|---|
| `/app/solicitudes` (lista) | Paciente | G2 — sin `GET` de listado en `solicitud-service` |
| `/app/dispositivos` | Paciente | G1 — `monitoring-service` excluye explícitamente al rol `patient` (403), y no hay listado de dispositivos en ningún servicio |
| `/app/teleconsultas` (lista/agenda) | Paciente, Profesional | G3 — sin `GET` en `teleconsult-service` |
| `/app/teleconsultas/:id/cierre` | Profesional | G3 — sin endpoint de cierre ni de guardado de diagnóstico |
| `/app/recursos` | Admin Centro | G13 — sin API de disponibilidad de profesionales/camas/servicios |
| `/app/admin/centros` (listado completo), `/app/admin/centros/:id` | Admin SAMR | G6 — sin `GET` de listado con los 3 estados ni detalle por id |
| `/app/admin/dispositivos` (listado), `/app/admin/dispositivos/:id` | Admin SAMR | G6 — sin ningún `GET` de dispositivos |
| `/app/auditoria/:id` como ruta con fetch propio | DPD | El detalle sale del mismo `GET /decisions/` ya cargado — no hay `GET /decisions/<id>/` individual |

## 2.2 Jerarquía de páginas (profundidad)

| Nivel | Ejemplo | Regla |
|---|---|---|
| **0 — Shell** | `/app` | Navbar + Sidebar persistentes; nunca se recarga entre navegaciones internas |
| **1 — Sección** | `/app/casos`, `/app/admin/centros` | Título de página + acciones primarias en el header de contenido |
| **2 — Listado → Detalle** | `/app/casos/:id` | Máximo 1 salto desde el listado; el detalle siempre puede volver al listado con el filtro/scroll conservado |
| **3 — Subacción de detalle** | `/app/casos/:id/matching` | Solo cuando la subacción tiene su propio flujo multi-paso; si es una sola pantalla, va en un modal, no en una ruta nueva |

**Regla de profundidad máxima: 3 niveles.** Si una funcionalidad necesita un 4º nivel, es señal de que debe ser un modal, un drawer o una pestaña dentro del detalle — no una ruta nueva.

## 2.3 Organización de contenidos

- **Por urgencia antes que por módulo**: en el dashboard de cada rol, lo primero visible es lo más urgente (emergencia activa, caso crítico, alerta), no el módulo "de moda". La jerarquía visual de urgencia (doc 05) manda sobre la jerarquía de navegación.
- **Contexto de paciente persistente**: cualquier pantalla que muestre a un paciente específico (`/app/pacientes/:id/*`, `/app/casos/:id`) debe mostrar un header de contexto fijo (nombre, edad, nivel de riesgo actual) mientras se navega entre sub-secciones relacionadas a ese caso.
- **Separación lectura/escritura administrativa**: `/app/admin/centros/*` y `/app/admin/dispositivos/nuevo` (administrador, alta) son rutas propias del rol `system_admin` — refleja la responsabilidad de M4 en la arquitectura. (El equivalente de lectura para el paciente, `/app/dispositivos`, se retiró del sitemap — ver G1.)
- **Un solo "historial clínico" conceptual**: `/app/historial` (paciente ve el suyo) y `/app/pacientes/:id/historial` (profesional/paramédico ven el de un paciente) son la misma plantilla de UI con distinto scope de datos — pero **ambas son de solo lectura hoy** (G12): ningún rol tiene un endpoint para escribir directamente en el historial.

## 2.4 Relación entre módulos (mapeo M1–M4 → IA)

| Módulo de negocio | Secciones de la IA que lo implementan | Roles que interactúan | Nivel de soporte |
|---|---|---|---|
| **M1 — Solicitud** | `/app/solicitudes/nueva`, `/app/solicitudes/:id`, `/app/ayuda` | Paciente/Familiar | 🟡 crear funciona, consultar estado no (G2) |
| **M2 — Evaluación y Asignación** | `/app/casos/*`, `/app/casos/:id/matching` | Profesional de Salud | 🟡 evaluación de solo lectura, matching sin elegir centro (G5) |
| **M3 — Atención** | `/app/teleconsultas/:id`, `/app/emergencias/*` | Paciente, Profesional, Paramédico | 🟡 emergencia sólida; teleconsulta solo creación+sala, sin cierre (G3) |
| **M4 — Integración e Interoperabilidad** | `/app/historial`, `/app/pacientes/:id/historial`, `/app/admin/*`, `/app/auditoria` | Todos (historial), Admin SAMR, DPD | 🟡 historial de solo lectura; admin sin listados (G6); auditoría sin filtros server-side |
| **Transversal (auth)** | `/login`, `/registro`, `/app/configuracion/*` | Todos | 🟡 login/registro sólidos; recuperar contraseña y notificaciones sin backend (G11, G7) |

## 2.5 Sidebar — ítems visibles por rol

| Ítem de sidebar | Paciente | Profesional | Paramédico | Admin Centro | Admin SAMR | DPD |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Dashboard | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Solicitudes (nueva) | ✔ | | | | | |
| Casos | | ✔ | | ✔ | | |
| Emergencias | ✔ | ✔ | ✔ | | | |
| Teleconsultas | ✔ (si tiene enlace) | ✔ | | | | |
| Historial clínico | ✔ (propio, lectura) | ✔ (por paciente, lectura) | ✔ (por paciente, lectura) | | | |
| Centros médicos (alta) | | | | | ✔ | |
| Dispositivos (alta) | | | | | ✔ | |
| FAQ (gestión) | | | | | ✔ | |
| Auditoría IA | | | | | | ✔ |
| Notificaciones | 🔴 pendiente (G7) — no se muestra hasta que exista backend | | | | | |
| Configuración | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |

**Nota**: "Recursos del centro" y "Dispositivos (lectura para paciente)" se retiraron del sidebar — no tienen ningún endpoint que los alimente (G13, G1).

## 2.6 Navbar (global, todo rol autenticado)

De izquierda a derecha: **logo/marca** (vuelve a `/app/dashboard`) · **breadcrumb contextual** (oculto en mobile) · *spacer* · **indicador de conectividad** (visible solo si degradada/offline) · **campana de notificaciones** con badge de conteo · **avatar + menú** (Perfil, Configuración, Cerrar sesión).

En roles con emergencia activa asignada (Paramédico, Paciente con emergencia en curso), el navbar muestra una **barra de estado de emergencia fija** debajo del navbar principal, no removible hasta que la emergencia se resuelva.

## 2.7 Breadcrumb — reglas

- Se muestra desde el nivel 2 en adelante (`Casos / #4821 / Matching`), nunca en el dashboard ni en listados de nivel 1.
- Cada segmento es clickeable excepto el actual.
- En mobile se colapsa a solo "← Volver a Casos" (un nivel atrás), no la ruta completa — prioriza espacio sobre completitud jerárquica.

## 2.8 Flujo de navegación — diagrama textual

```
Login ──→ Dashboard (según rol, mismo payload BFF para todos hoy — G8)
             │
             ├─(Paciente)─→ Nueva solicitud ─→ [respuesta inmediata del POST] ─→ (sin forma de re-consultar estado — G2)
             │                    │
             │                    └─(anomalía IoT)─→ Emergencia activa ─→ Guía primeros auxilios (texto estático, sin espera)
             │
             ├─(Profesional)─→ Casos (cola global) ─→ Detalle caso (solo lectura) ─→ Matching (1 clic, sin elegir centro) ─→ Teleconsulta (crear+entrar)
             │                                                                                                              └─(sin cierre posible — G3)
             │                    └─(vía emergencia)─→ Emergencia despachada ─→ Cierre de caso (solo professional — G9)
             │
             ├─(Paramédico)─→ Emergencias (cola) ─→ Despachar ─→ Historial del paciente (solo lectura — G12)
             │
             ├─(Admin Centro)─→ Casos (ver) ⇄ Verificar completitud (sin poder cerrar — G9)
             │
             ├─(Admin SAMR)─→ Registrar centro ─→ [validación automática invisible — G6] ─→ (solo se confirma si aparece luego en "disponibles")
             │                    ├─→ Registrar dispositivo ─→ [sin confirmación posterior — G6]
             │                    └─→ Gestionar FAQ (nuevo, soportado)
             │
             └─(DPD)─→ Auditoría (lista de 100, sin filtros server-side) ─→ Marcar revisión (revisado/observado, sin "pendiente" ni "rechazado")
```

Toda ruta autenticada que reciba un rol sin permiso redirige a `/403` (ver doc 11), nunca a `/login` de nuevo si la sesión es válida — la ambigüedad entre "no tienes sesión" y "no tienes permiso" es una fuga de confianza que se evita explícitamente.
