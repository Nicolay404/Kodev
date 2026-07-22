# 00 - Alineación con el Backend Real
## SAMR - Auditoría de la documentación UX/UI contra la implementación

> **Por qué existe este documento.** Los documentos 01–14 se escribieron a partir de la documentación de arquitectura (`ARQUITECTURA_MAESTRA_SAMR_v4.md`, SRS, casos de uso) - es decir, el diseño **previsto**. Este documento se escribió después de leer el código real del backend (rama `origin/main`, carpeta `samr/`, 13 microservicios Django/DRF + BFF FastAPI), y registra cada punto donde la implementación **actual** diverge de lo previsto. Cada corrección aplicada en los docs 01–14 cita una entrada de este documento (`ver 00 §X.Y`).
>
> **Método**: todo el análisis se hizo leyendo `models.py`, `views.py`, `urls.py`, `serializers.py`, `permissions.py`, `services.py`, `events/publisher.py`, `events/consumer.py` y `README.md` de cada servicio directo del historial de git (`git show origin/main:<ruta>`), sin ejecutar el backend. Es un análisis estático - no reemplaza pruebas de integración, pero es preciso respecto al código tal como está escrito.
> **Fecha del análisis**: sobre el commit `9f04a6b` ("feat(core-services): complete backend MVP") y posteriores en `origin/main`.

---

## 0.1 Confirmado sin cambios - lo que el backend sí respalda tal como se diseñó

| Elemento del diseño | Confirmación en backend |
|---|---|
| **6 roles exactos**: `patient, professional, nurse, center_admin, system_admin, dpd_delegate` | `auth-service/apps/auth/models.py`, `ROLE_CHOICES` - coincide 1:1 con las 6 personas del doc 01 (Familiar del Paciente sigue siendo un [SUPUESTO] de UX sobre una cuenta `patient`, no un rol de backend distinto - confirmado, no existe rol `familiar`) |
| **4 niveles de riesgo clínico**: crítico/alto/medio/bajo | `evaluacion-service/apps/evaluacion/models.py::Evaluacion.LEVELS` |
| **Auditoría exclusiva del rol `dpd_delegate`** | `audit-service/apps/audit/permissions.py::IsDPDDelegate` - confirmado, 403 para cualquier otro rol (test `test_other_role_forbidden`) |
| **Emergencia: solo el paciente reporta, solo personal clínico despacha** | `emergency-service/apps/emergency/views.py` - `POST /` exige `rol=="patient"`; `POST /dispatch/` exige rol en `{professional,nurse,center_admin,system_admin}` |
| **Registro/validación de centros y dispositivos exclusivo de `system_admin`** | `admin-integracion-service/apps/admin_integ/permissions.py::IsSystemAdmin` |
| **Bloqueo de cuenta tras intentos fallidos** | `auth-service` - 5 intentos → `locked_until`, HTTP 429 |
| **Consentimientos LOPDP** (`consent_data`, `consent_ai`, `consent_sharing`) | `patient-service/apps/patient/models.py::Patient` - los 3 campos existen tal como se diseñaron en doc 04/10 |
| **Cifrado de cédula** | `patient-service` cifra con Fernet, nunca persiste texto plano - coincide con doc 09/12 |

---

## 0.2 Brechas críticas - funcionalidad diseñada sin endpoint de backend

Estas son las correcciones de mayor impacto. Cada una **bloquea** una parte del flujo tal como estaba diseñado, no es solo un matiz.

### G1 - El paciente no puede ver sus propias alertas ni signos vitales
`monitoring-service/apps/monitoring/views.py::AlertView` exige rol en `{professional, nurse, center_admin, system_admin}` - **excluye explícitamente `patient`** (403). El WebSocket `MonitoringConsumer.ALLOWED_ROLES` hace lo mismo. Además, no existe ningún endpoint que liste los dispositivos vinculados a un paciente (el "registro" de dispositivo en `monitoring-service` vive solo en caché Redis, sin modelo persistente; y `admin-integracion-service::Device` no tiene ningún `GET`).
**Impacto**: la pantalla `/app/dispositivos` (doc 02/04, vista paciente de solo lectura) no tiene ningún dato que mostrar - ni sus alertas ni sus dispositivos son consultables por el propio paciente.
**Corrección aplicada**: se retira `/app/dispositivos` del sitemap del paciente; se documenta como brecha a resolver (doc 14, prioridad alta).

### G2 - El paciente no puede consultar el estado de su solicitud
`solicitud-service` no tiene **ningún** endpoint `GET` - ni para listar solicitudes propias ni para ver el detalle de una. El único dato que el frontend puede conocer es la respuesta inmediata del `POST /` (estado inicial `"pendiente"`). Los estados posteriores (`validada`, `rechazada`, `pendiente_reintento`) existen en la base de datos pero son **invisibles vía API**.
**Impacto**: el stepper "Enviada → Validando → Evaluando → Asignada" (doc 03 §3.4, doc 04 §4.4) no es implementable con el backend actual, salvo el paso final: `evaluacion-service` sí expone `GET /api/evaluacion/riesgo/<solicitud_id>/`, que devuelve 200 con el riesgo si ya fue evaluada, o 404 si no. Es la única señal de progreso real disponible hoy, y requiere que el cliente ya conozca el `solicitud_id` (lo recibe en la respuesta del `POST` original).
**Corrección aplicada**: el stepper se simplifica a 2 estados verificables (`Enviada` → `Riesgo evaluado: {nivel}` vía polling a `/riesgo/`), con el resto marcado explícitamente como no disponible hoy (doc 03/04/11).

### G3 - No existe forma de cerrar una teleconsulta ni registrar diagnóstico
`teleconsult-service` solo implementa `POST /api/teleconsult/` (crear sesión). No hay `GET` (ni lista ni detalle), no hay endpoint de cierre, `diagnosis` y `ai_recommendation` no se escriben desde ningún código del servicio, y **el evento `teleconsult.closed` que `cierre-caso-service` espera consumir nunca se publica** - confirmado revisando ambos servicios. Consecuencia: un `Caso` solo puede crearse hoy por la vía de emergencia (`emergency.dispatched`, que sí se publica); **el camino "teleconsulta → cierre de caso" está roto de punta a punta en el backend actual**, no solo en el frontend.
**Impacto**: `/app/teleconsultas` (lista), `/app/teleconsultas/:id/cierre`, y el "resumen post-consulta con diagnóstico" (doc 04 §4.6) no tienen soporte de backend.
**Corrección aplicada**: se retira `/app/teleconsultas` (lista) del sitemap; `/app/teleconsultas/:id` se mantiene solo como la sala de señalización WebRTC (que sí funciona) sin flujo de cierre; se documenta como la brecha más crítica del sistema (doc 14, prioridad máxima - bloquea todo el módulo M3 no-emergencia).

### G4 - El paciente no tiene forma de descubrir el `room_token` de su teleconsulta
Ni siquiera si G3 no existiera: el WebSocket de señalización requiere `room_token` en la URL (`ws/teleconsult/<room_token>/`), y ese token solo se conoce en el momento de la creación (respuesta del `POST`, que hace el profesional/admin, no el paciente) - no hay ningún endpoint para que el paciente lo consulte después.
**Impacto**: el flujo "el paciente recibe notificación y toca 'Unirme a la consulta'" no es realizable sin que ese token viaje por otro canal.
**Corrección aplicada**: documentado junto a G3 como parte de la misma brecha; se propone como recomendación de backend (doc 14).

### G5 - El matching no permite elegir centro médico
`MatchingRequestSerializer` solo acepta `patient_id` y `professional_id` (opcional según rol) - **no acepta `center_id`**. `find_best_center()` elige automáticamente el primer centro disponible por orden alfabético (no por especialidad, distancia, ni nivel de riesgo), y `mvp_matching_score()` devuelve siempre `Decimal("100.00")` - una constante, no un score real.
**Impacto**: la pantalla `P-Matching` diseñada como "lista de centros candidatos, el profesional elige y confirma" (doc 04 §4.5) no coincide con el backend: es un único botón de acción, resultado inmediato (asignado o 409 sin centro disponible).
**Corrección aplicada**: `P-Matching` se rediseña como acción de un solo paso con resultado síncrono (doc 04), se elimina la lista de candidatos y el estado "confirmando disponibilidad" (era asíncrono en el diseño original; en realidad es una sola llamada síncrona).

### G6 - Administración de centros y dispositivos sin listado ni detalle
`admin-integracion-service` solo expone: `POST /centers/register/`, `GET /centers/available/` (solo centros ya `validated`, requiere token de servicio o `system_admin`), `POST /devices/register/`. **No existe** `GET` de listado general de centros (con sus 3 estados), ni `GET /centers/<id>/` de detalle, ni ningún `GET` de dispositivos. La validación de un centro es automática e instantánea (Celery `.delay()` resuelto por una variable de entorno fija, no una revisión real) - pero **no hay ninguna forma de que el admin verifique el resultado** salvo que el centro aparezca más tarde en `/centers/available/` (positivo) - un rechazo es completamente invisible vía API.
**Impacto**: `/app/admin/centros` (listado con estados), `/app/admin/centros/:id` (detalle/reenvío tras rechazo), `/app/admin/dispositivos` (listado) no tienen soporte de backend.
**Corrección aplicada**: se retiran los listados/detalle del sitemap; se conserva únicamente el formulario de registro (que sí funciona) con una confirmación de envío, sin seguimiento posterior; brecha documentada en doc 14 como alta prioridad.

### G7 - Notificaciones sin backend real
`notification-service` no tiene modelos, no tiene un solo endpoint HTTP, y su único "canal" es `MVPLogNotificationAdapter`, que hace `logger.info(...)` - no hay FCM, no hay WebSocket de notificaciones, no hay ninguna forma de que el frontend liste, marque como leída o reciba en tiempo real una notificación.
**Impacto**: `/app/notificaciones` (doc 02/04) no tiene ningún dato real que consumir.
**Corrección aplicada**: se conserva la especificación de la pantalla (útil como blueprint), pero se marca explícitamente "Pendiente de backend" en el sitemap y wireframes, y se eleva como recomendación de alta prioridad (doc 14) - es la única brecha donde se decidió no retirar el diseño, porque el patrón de notificaciones ya está referenciado transversalmente en toda la documentación (alertas críticas, resultados de validación, etc.) y sirve como especificación lista para cuando exista el backend.

### G8 - El dashboard (BFF) no está diferenciado por rol
`bff-service` expone un único `GET /dashboard/` que agrega siempre las mismas 4 llamadas (`/api/patients/me/`, `/api/evaluacion/mis-casos/`, `/api/monitoring/alerts/`, `/api/cierre-caso/mis-casos/`), sin importar el rol del usuario autenticado. Para un `professional`, por ejemplo, `GET /api/patients/me/` no tiene sentido (ese endpoint es específicamente del rol `patient`) y devolvería error; para un `patient`, `GET /api/monitoring/alerts/` siempre da 403 (G1).
**Impacto**: el diseño "el dashboard varía 100% por rol, con KPIs y secciones distintas" (doc 04 §4.3) no puede alimentarse desde este único endpoint del BFF tal como está.
**Corrección aplicada**: doc 04 se actualiza para aclarar que, mientras el BFF no soporte agregación por rol, el frontend debe: (a) para el rol `patient`, usar el BFF tal cual (es el único rol para el que las 4 llamadas tienen sentido, salvo `monitoring` que siempre fallará por G1); (b) para los demás roles, consumir los endpoints de cada microservicio directamente a través del gateway, sin pasar por el BFF. Documentado como recomendación de backend (doc 14).

### G9 - Cierre de caso: solo `professional`, no `center_admin`
`cierre-caso-service/apps/cierre/views.py::CierreCasoView` exige literalmente `rol == "professional"` - cualquier otro rol, incluido `center_admin`, recibe 403.
**Impacto**: doc 03 §3.9 y doc 02 (sidebar) asignaban esta acción también a "Administrador de Centro Médico".
**Corrección aplicada**: se retira la capacidad de cierre de caso del rol Administrador de Centro Médico en todos los documentos; ese rol conserva `/app/casos` (ver) y `GET .../verify/` (verificar completitud sin cerrar), pero el botón "Cerrar caso" solo aparece para `professional`. *(Nota: `/app/recursos` también se retiró del sitemap de este rol por una brecha distinta - ver §G13 - dejándolo con una superficie funcional real muy reducida; ver doc 14 §14.0.)*

### G11 - No existe recuperación de contraseña
`auth-service` expone exactamente 4 endpoints: `POST /register/`, `POST /login/`, `POST /token/refresh/`, `GET /me/`. No hay `POST /password-reset/` ni equivalente - ningún envío de código, ninguna verificación, ningún cambio de contraseña sin sesión activa.
**Impacto**: el flujo completo `/recuperar-contrasena` (3 pantallas, doc 03 §3.3, doc 04 §4.2) no tiene ningún soporte de backend.
**Corrección aplicada**: se marca todo el flujo como "Pendiente de backend" en el sitemap; se conserva el diseño (es una expectativa básica de cualquier producto con login) y se eleva en doc 14 como recomendación de alta prioridad.

### G12 - El historial clínico no tiene ningún endpoint de escritura
`historial-interop-service` solo implementa `GET /historial/<patient_id>/` y `GET /history/fhir/<patient_id>/`. No existe ningún `POST`/`PATCH` para que un profesional o paramédico agregue una nota o actualice el historial manualmente - la única forma en que el historial cambia es automática, al consumir el evento `caso.cerrado`.
**Impacto**: "el paramédico actualiza el historial clínico en campo" (doc 01 Persona 4, doc 02/03 M3) no es una acción disponible - el paramédico solo puede **leer**, nunca escribir directamente.
**Corrección aplicada**: se retira la capacidad de "actualizar historial" como acción directa del paramédico/profesional en todos los documentos; se aclara que el historial se actualiza únicamente como efecto secundario de cerrar un caso (acción exclusiva de `professional`, ver G9).

### G13 - No existe gestión de recursos/disponibilidad del centro médico
Ningún servicio expone un endpoint de "disponibilidad de profesionales, camas o servicios" de un centro. El modelo `Professional` existe en la base de datos de `admin-integracion-service` (con campos `available`, `current_load`) pero **no tiene serializer, vista ni URL** - es inaccesible vía API en esta iteración.
**Impacto**: `/app/recursos` (doc 02, rol Administrador de Centro Médico) no tiene ningún dato que leer o escribir.
**Corrección aplicada**: se retira `/app/recursos` del sitemap soportado; se documenta como brecha de alta prioridad en doc 14, dado que sin esto el rol `center_admin` queda con muy poca superficie funcional real (solo puede ver casos y verificar completitud, no puede cerrar por G9).

### G14 - No existe cambio de contraseña ni gestión de sesiones activas
Ningún endpoint de `auth-service` permite cambiar la contraseña estando autenticado, ni cerrar sesión del lado del servidor (el JWT es stateless - "cerrar sesión" solo puede significar "descartar el token en el cliente"), ni listar/revocar sesiones activas en otros dispositivos.
**Impacto**: `/app/configuracion/seguridad` (doc 02/04) no puede ofrecer "cambiar contraseña" ni "sesiones activas" tal como se diseñó.
**Corrección aplicada**: se simplifica esa pantalla a lo que sí es real (cerrar sesión = borrar el token localmente); se documenta la brecha en doc 14.

### G10 - Acceso al historial clínico sin restricción por relación de cuidado
`historial-interop-service::can_read()` permite a **cualquier** usuario con rol `professional`, `nurse` o `center_admin` leer el historial de **cualquier** paciente - no verifica que ese profesional esté (o haya estado) asignado al caso del paciente.
**Impacto**: no invalida ninguna pantalla, pero sí una afirmación de seguridad implícita en el diseño original (doc 03 §3.10 asumía "sin relación de atención activa → 403").
**Corrección aplicada**: doc 03 §3.10 se corrige para reflejar el comportamiento real (no hay ese chequeo hoy) y se marca como hallazgo de seguridad a escalar - no es una decisión de UX, es una brecha de control de acceso del backend que excede el alcance de este paquete pero debe quedar registrada.

---

## 0.3 Correcciones menores - el backend funciona distinto en el detalle

| # | Elemento | Diseño original | Comportamiento real del backend |
|---|---|---|---|
| M1 | Guía de primeros auxilios | "Generada por IA para el caso específico", con estado de carga ("Preparando instrucciones para tu situación…") | `emergency-service` usa un **texto estático fijo** (`settings.MVP_FIRST_AID_GUIDE`), igual para cualquier paciente/triage - no hay generación, por lo tanto no hay espera real que comunicar |
| M2 | "Mis casos" (profesional) | Cola personal, filtrada por profesional asignado | `evaluacion-service` y `cierre-caso-service` devuelven los **50 registros más recientes de todo el sistema** sin filtrar por profesional - es una cola compartida, no personal |
| M3 | Ajuste manual del nivel de riesgo por el profesional | El profesional puede sobreescribir el nivel calculado por IA, con motivo | No existe ningún endpoint de actualización (`PATCH`/`PUT`) sobre `Evaluacion` - el nivel de riesgo es inmutable una vez creado |
| M4 | Reasignación automática si el centro no confirma | Sistema sugiere automáticamente el siguiente candidato | No existe: si no hay centro disponible, se publica `matching.fallido` y se responde 409; no hay cola de reintento ni sugerencia automática |
| M5 | Checklist de cierre de caso | Multi-campo (diagnóstico, notas, datos del paciente) | La verificación real (`verify_case()`) solo exige 2 cosas: `clinical_notes` no vacío + que exista `teleconsult_id` o `emergency_id` - mucho más simple de lo diseñado |
| M6 | Auditoría - filtros por fecha/módulo/nivel de riesgo | Filtros server-side | `GET /decisions/` no acepta ningún query param - devuelve los 100 más recientes sin filtrar; cualquier filtro debe aplicarse client-side sobre esos 100 |
| M7 | Estados de revisión DPD | pendiente/revisado/observado, con "rechazado" implícito en algunos flujos | Solo `revisado` y `observado` son alcanzables vía API (el serializer de entrada no acepta `"pendiente"`); no existe estado "rechazado" |
| M8 | Timeline de historial clínico | Múltiples tipos de evento (solicitud, teleconsulta, emergencia, decisión IA) | El historial solo acumula eventos `caso.cerrado` - es una lista de casos cerrados, no un registro granular de cada paso clínico |
| M9 | Auditoría de decisiones de IA | Alcance: solo decisiones de IA | El consumidor de `audit-service` se suscribe a `#` (**todos** los eventos del bus, incluido `auth.login_success`) - es un log de auditoría general, más amplio de lo que su nombre de módulo sugiere |
| M10 | Inmutabilidad del log de auditoría | "Append-only a nivel de motor" (`REVOKE UPDATE/DELETE`) | Solo hay una guarda a nivel de aplicación (`AuditLog.save()`); no hay ningún `REVOKE` en las migraciones - la inmutabilidad no está garantizada a nivel de base de datos todavía |

---

## 0.4 Funcionalidad que el backend sí soporta y no estaba en el diseño original

| Funcionalidad | Evidencia en backend | Dónde se agrega en la documentación corregida |
|---|---|---|
| Gestión de FAQ (crear/editar) por `system_admin` | `solicitud-service` - `POST`/`PATCH /api/solicitud/faq/`, restringido a `rol=="system_admin"` | Nueva pantalla en doc 02/04: `/app/admin/faq` |
| Derecho al olvido - borrar una conversación del chatbot | `DELETE /api/solicitud/conversations/<id>/`, solo el dueño | Ya estaba en el copy deck (doc 10 §10.4); se agrega el punto de entrada explícito en doc 03/04 (menú de la conversación) |
| Verificación de completitud de un caso sin cerrarlo | `GET /api/cierre-caso/<id>/verify/`, roles `professional/center_admin/system_admin` | Ya estaba conceptualmente en doc 04 (checklist); se ajusta para reflejar que es una consulta explícita separada del cierre |
| Listado de emergencias propias (paciente) vs. todas (clínico) | `GET /api/emergencies/`, filtrado automático por rol | Se mantiene, ya estaba correctamente diseñado; se agrega explícitamente `/app/emergencias` (lista) también para el rol Paciente y Profesional, que el sitemap original no exponía como ruta de listado |

---

## 0.5 Nota sobre el carácter "MVP" del backend

Varias piezas que el nombre del servicio sugiere como inteligencia artificial real son, explícitamente en el propio código (comentarios y flags como `clinical_validation: false`, `adapter: "mvp_..."`), simuladores deterministas:

- **Chatbot de síntomas**: matcher de similitud de texto (Jaccard) contra una base de FAQ administrada manualmente - no es un LLM.
- **Evaluación de riesgo**: reglas de palabras clave configurables por variable de entorno - no es un modelo de IA ni usa RAG.
- **Validación del Consorcio** (solicitud) y **validación de centro médico** (admin): el resultado depende de una variable de entorno fija (`MVP_CONSORTIUM_OUTCOME`, `MVP_CENTER_VALIDATION_OUTCOME`), no de una integración real.
- **Guía de primeros auxilios**: texto estático, no generado.

**Implicación de diseño**: todo el copy que en los docs 01–14 sugiere "la IA analiza tu caso específico" sigue siendo válido como **intención de producto** (es lo que el sistema debe hacer cuando la IA real se integre), pero el equipo de frontend debe saber que hoy el contenido detrás de esos mensajes es fijo/determinista. No se cambió el copy dirigido al usuario final por este motivo - sería prematuro optimizar la experiencia alrededor de una limitación temporal del MVP - pero se documenta aquí para que nadie interprete la ausencia de personalización real como un bug de frontend.

---

## 0.6 Resumen ejecutivo - qué cambió en cada documento

| Doc | Cambios aplicados |
|---|---|
| 01 | Roles confirmados (ya no son supuesto); nota de brecha en journey de solicitud y teleconsulta |
| 02 | Sitemap: retira `/app/dispositivos` (paciente), `/app/teleconsultas` (lista), `/app/admin/centros` y `/app/admin/dispositivos` (listado/detalle); agrega `/app/admin/faq`; marca `/app/notificaciones` como pendiente de backend; nota sobre dashboard no diferenciado por rol |
| 03 | Flujos de solicitud, matching, teleconsulta, cierre de caso, admin de centros/dispositivos y auditoría corregidos para reflejar endpoints reales |
| 04 | Wireframes de P-Solicitud-Detalle, P-Matching, P-Sala-Teleconsulta, P-Admin-* y P-Auditoria-Lista corregidos |
| 05 | Nota sobre `Alert.severity` (solo "crítico" se produce en la práctica) |
| 06 | Componente de Matching simplificado (sin lista de candidatos) |
| 10 | Copy de "generando guía" retirado (la guía es estática/instantánea) |
| 11 | Estados de Matching, Teleconsulta y Admin ajustados a comportamiento síncrono/limitado real |
| 12 | Nota sobre BFF de solo lectura (mutaciones van directo al gateway) y claim JWT `rol` (no `role`) |
| 13 | Nuevo bloque de checklist "Alineación con backend" |
| 14 | Nueva sección de brechas críticas de backend, priorizada por bloqueo funcional |
