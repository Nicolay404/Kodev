# 03 — User Flows
## SAMR — Sistema de Atención Médica Remota

> Convención: cada flujo lista **Happy Path** (pasos numerados), **Edge Cases** (situaciones válidas pero no ideales), **Casos de Error** (algo falla) y **Estados Alternativos** (variaciones legítimas del flujo). Los IDs de pantalla (`P-01`, `P-02`...) se referencian en el doc 04 (Wireframes).

---

## 3.1 Autenticación — Registro

**Happy Path**
1. Usuario entra a `/registro` → **P-Registro**.
2. Completa: nombre, email o cédula, teléfono, contraseña, confirmación.
3. Acepta consentimientos LOPDP obligatorios (datos, uso de IA) — checkbox separado del de compartición (opcional).
4. Envía → validación en tiempo real por campo mientras escribe (no solo al enviar).
5. Sistema crea cuenta, envía verificación (email o SMS).
6. Usuario verifica → redirige a `/app/dashboard` con onboarding breve (ver doc 10).

**Edge Cases**
- Usuario ya tiene cuenta con ese email → mensaje específico con link directo a "Iniciar sesión" (no un error genérico).
- Usuario es adulto mayor sin email → alternativa de registro por teléfono + SMS.
- Familiar registra en nombre de un paciente que no puede operar el sistema → flujo de "cuenta de cuidador" *(ver [SUPUESTO] en doc 01, §1.5)*.

**Casos de Error**
- Contraseña no cumple política → error inline específico ("mínimo 8 caracteres, incluye un número"), no genérico.
- Falla de red al enviar → mensaje "No pudimos conectar. Tus datos no se perdieron, intenta de nuevo." + botón reintentar (nunca perder lo ya escrito).
- Verificación expira → botón "Reenviar código" con cooldown visible.

**Estados alternativos**
- Registro incompleto abandonado → si vuelve dentro de 24h, ofrece continuar donde quedó (borrador local).

---

## 3.2 Autenticación — Login

**Happy Path**
1. `/login` → **P-Login**: campos email/teléfono + contraseña.
2. Envía → sistema valida → redirige a `/app/dashboard`.

**Edge Cases**
- 5 intentos fallidos → cuenta bloqueada temporalmente (RNF-01) → mensaje explícito con tiempo de espera, no "inténtalo más tarde" ambiguo.
- Sesión expirada mientras usaba la app → redirige a login preservando la ruta destino, sin perder el trabajo en curso si había un formulario abierto (aviso antes de redirigir).

**Casos de Error**
- Credenciales incorrectas → mensaje neutro "Email o contraseña incorrectos" (nunca especificar cuál, por seguridad).
- Cuenta bloqueada → mensaje con opción directa a "Recuperar contraseña".

---

## 3.3 Autenticación — Recuperar contraseña

> ⚠️ **Pendiente de backend** ([00](00-alineacion-backend.md) §G11): `auth-service` no tiene ningún endpoint de recuperación de contraseña. El flujo completo queda especificado para cuando exista, pero no debe implementarse contra un mock — es una de las brechas de mayor prioridad (doc 14).

**Happy Path**
1. `/recuperar-contrasena` → ingresa email/teléfono.
2. Sistema envía código → `/recuperar-contrasena/verificar`.
3. Ingresa código → `/recuperar-contrasena/nueva` → define nueva contraseña → confirma → login automático.

**Edge Cases**
- Email no existe en el sistema → mismo mensaje de éxito que si existiera ("Si el correo existe, enviamos instrucciones") — evita enumeración de cuentas.

**Casos de Error**
- Código incorrecto → error inline, 3 intentos antes de invalidar el flujo y forzar reinicio.
- Código expirado → mensaje claro + botón reenviar.

---

## 3.4 M1 — Reportar síntomas y registrar solicitud (Paciente/Familiar)

> ⚠️ **Brecha de backend** ([00](00-alineacion-backend.md) §G2): `solicitud-service` no tiene ningún `GET` — ni lista ni detalle. Los pasos 5–7 de abajo describen lo que el producto **debería** comunicar; lo que el backend permite hoy son solo los pasos 5 (respuesta inmediata del `POST`) y 7 (única señal real, vía polling a `evaluacion-service`). El paso 6 ("Validada, evaluando riesgo") no tiene ninguna fuente de datos hoy — se mantiene documentado porque el estado sí existe en la base de datos, solo falta el endpoint para leerlo.

**Happy Path**
1. `/app/solicitudes/nueva` → **P-Chat-Solicitud**: chatbot pregunta motivo de consulta (`POST /api/solicitud/chat/`).
2. Usuario describe síntomas en lenguaje natural o selecciona de sugerencias rápidas.
3. Bot pide datos complementarios estructurados (duración, intensidad) vía formulario corto embebido en el chat.
4. Si tiene dispositivo IoT vinculado, sistema pre-completa datos biomédicos automáticamente (visible, editable con aviso). *(Nota: esto depende de que el dato ya esté disponible en el cliente — el paciente no puede consultar sus propios dispositivos, ver G1; el pre-llenado solo es posible si el dato llegó por otra vía, ej. el propio flujo de monitoreo en tiempo real si el paciente estuviera conectado al mismo dispositivo.)*
5. Usuario confirma y envía (`POST /api/solicitud/`) → **P-Solicitud-Detalle** muestra estado "Enviada" con los datos que el propio `POST` devolvió — es la única fuente de verdad disponible en este momento.
6. *(No implementable hoy — ver brecha arriba.)* Conceptualmente: "Validada, evaluando riesgo".
7. El frontend hace polling a `GET /api/evaluacion/riesgo/{solicitud_id}/`: 404 mientras no haya evaluación, 200 con `nivel_riesgo` cuando ya la hay → única actualización de estado real y verificable que puede mostrarse tras el paso 5.

**Edge Cases**
- Usuario no tiene dispositivo IoT vinculado → el paso 4 se omite sin fricción, formulario pide los datos manualmente con ayuda contextual ("¿No tienes un dispositivo? Puedes ingresar los datos manualmente").
- Usuario abandona el chat a medias → el borrador solo puede conservarse **localmente** (localStorage/estado de cliente) — no hay forma de recuperarlo desde el servidor si cambia de dispositivo, porque no hay `GET` de conversaciones abiertas.
- Reporte ambiguo que el bot no entiende → el chatbot es un comparador de similitud de texto contra una base de FAQ (no un LLM real, ver [00](00-alineacion-backend.md) §0.5); si la confianza es menor a un umbral, la propia API marca la respuesta como `source: "human_escalation"` con un texto de fallback fijo — el frontend debe mostrar ese fallback tal cual, no inventar una respuesta alternativa.

**Casos de Error**
- El motor de orientación (chatbot) responde con baja confianza → mostrar el texto de escalación a humano que la API ya devuelve (`source: "human_escalation"`), no un timeout genérico — la respuesta siempre llega, no hay estado de "esperando IA" real de varios segundos.
- Solicitud rechazada por datos incompletos → mensaje específico de qué falta; como no hay `GET` de detalle, la única oportunidad de corregir es en el mismo formulario antes de enviar (validar en cliente antes del `POST` para minimizar rechazos, ya que no hay forma de "editar y reenviar" una solicitud ya creada).

**Estados alternativos**
- **Flujo automático por anomalía IoT** (sin acción del usuario): `monitoring-service` detecta anomalía → publica `vitals.critical_detected` → `solicitud-service` la consume y crea la solicitud automáticamente (`fuente="iot_anomalia"`). El paciente **no recibe ninguna notificación de esto hoy** (G7, sin backend de notificaciones) — el único lugar donde podría enterarse es si la anomalía además crea una `Emergency` (ver §3.8), que sí tiene una pantalla real.

---

## 3.5 M2 — Evaluación de riesgo y escalamiento (vista Profesional de Salud)

**Happy Path**
1. `/app/casos` → **P-Cola-Casos**: `GET /api/evaluacion/mis-casos/` devuelve los 50 casos más recientes **de todo el sistema, no filtrados por profesional** ([00](00-alineacion-backend.md) §0.3 M2); el ordenamiento por nivel de riesgo (crítico primero) se hace **en el cliente** después de recibir la respuesta, no lo garantiza la API.
2. Profesional abre un caso → **P-Detalle-Caso**: `GET /api/evaluacion/riesgo/{solicitud_id}/` — ve síntomas, datos biomédicos, nivel de riesgo calculado, y `fuentes_rag` (en el MVP actual siempre el mismo objeto fijo `mvp_rules`, ver §0.5 — la UI debe mostrarlo igual, sin fingir variedad que no existe).
3. Si riesgo crítico, el backend ya publicó automáticamente `vity.escalation_requested` al momento de evaluar — no es una acción del profesional, es informativo (la UI puede reflejar "Escalado automáticamente").
4. Profesional decide: iniciar matching de recursos (único siguiente paso disponible — no existe endpoint para "solicitar más información al paciente").

**Edge Cases**
- Múltiples casos críticos simultáneos → cola permite fijar ("pin") un caso mientras se revisa otro sin perder contexto (comportamiento de cliente, no depende del backend).

**Casos de Error**
- `GET /riesgo/{solicitud_id}/` devuelve 404 → la solicitud existe pero aún no fue evaluada (no es un error real, es un estado "en cola de evaluación" — no mostrar como fallo).

> ⚠️ Se retiró el edge case "el profesional puede corregir el nivel de riesgo calculado": no existe ningún endpoint de actualización sobre `Evaluacion` — el nivel de riesgo es inmutable una vez creado ([00](00-alineacion-backend.md) §0.3 M3). Si el profesional discrepa clínicamente, hoy solo puede documentarlo en las notas del cierre de caso, no corregir el dato de IA.

---

## 3.6 M2 — Matching y asignación de recursos

> ⚠️ **Rediseñado contra backend real** ([00](00-alineacion-backend.md) §G5): `MatchingRequestSerializer` solo acepta `patient_id` y `professional_id` — **no existe `center_id` en la entrada**. El backend elige el centro automáticamente (`find_best_center()`: primer centro `disponible=True` por orden alfabético) y el score siempre es `100.00` (constante, no calculado). No hay lista de candidatos que mostrar ni elegir.

**Happy Path**
1. Desde el caso, profesional en `/app/casos/:id/matching` → **P-Matching**: un solo botón "Ejecutar matching" (no una lista de centros).
2. Profesional confirma → `POST /api/evaluacion/matching/{evaluacion_id}/` — llamada **síncrona**, no hay estado intermedio "confirmando disponibilidad".
3. Respuesta inmediata: `201` con el centro que el sistema asignó (nombre visible recién en la respuesta, no antes) → publica `recursos.asignados`.

**Edge Cases**
- Ningún centro disponible → `409` inmediato con `{"reason": "no_available_center"}` — mostrar "No hay centros disponibles en este momento", sin sugerir reintento automático (no existe) ni cola de espera (no existe). La única acción posible es que el profesional reintente manualmente más tarde.

**Casos de Error**
- Evaluación ya tiene un matching (`Matching` es 1:1 e inmutable) → `400`, mensaje "Este caso ya tiene recursos asignados" — no hay reasignación ni edición posible desde ningún endpoint.
- `professional_id` requerido y ausente (cuando quien ejecuta es `center_admin`/`system_admin`, no `professional`) → error inline pidiendo seleccionar el profesional antes de continuar.

---

## 3.7 M3 — Teleconsulta (Paciente + Profesional)

> 🔴 **Brecha crítica de backend** ([00](00-alineacion-backend.md) §G3, §G4) — la de mayor impacto de todo el paquete. `teleconsult-service` solo tiene `POST /api/teleconsult/` (crear). No hay `GET` (ni lista ni detalle), no hay endpoint de cierre, `diagnosis`/`ai_recommendation` nunca se escriben, y el evento `teleconsult.closed` que `cierre-caso-service` espera **nunca se publica**. El flujo de abajo distingue explícitamente lo que funciona hoy de lo que requiere que el backend agregue estos endpoints (recomendación de máxima prioridad, doc 14).

**Happy Path (Profesional/Admin — quien puede crear la sesión)**
1. Desde el caso, `POST /api/teleconsult/` con `patient_id` (y `professional_id` si quien crea es admin) → la respuesta `201` incluye el `room_token` generado — **este es el único momento en que ese token existe en el sistema del lado del cliente**.
2. El profesional entra directamente al WebSocket `ws/teleconsult/{room_token}/` con su JWT como query param → **P-Sala-Teleconsulta** (video/audio/texto vía WebRTC, señalización pass-through — esto sí funciona).
3. *(Sin endpoint de cierre — ver brecha.)* Al terminar, el profesional no tiene forma de guardar el diagnóstico ni cerrar formalmente la sesión vía API hoy.

**Happy Path (Paciente)** — ⚠️ solo funciona si el `room_token` le llegó por un canal fuera de esta documentación (hoy no hay ninguno soportado, ya que notificaciones tampoco tiene backend — G7):
1. Recibe el enlace/token por el canal que sea (fuera del alcance de backend actual).
2. Entra al mismo WebSocket con su propio JWT → la autorización del servidor exige que su `usuario_id` coincida con `patient_id` o `professional_id` de esa sesión — funciona igual que para el profesional una vez que tiene el token.
3. *(Sin resumen post-consulta — ver brecha: nada se guarda del lado del servidor.)*

**Edge Cases**
- Solo audio disponible (sin cámara) → degradación elegante a llamada de voz — esto es comportamiento 100% de cliente (WebRTC nativo), no depende del backend.
- Mensaje de señalización con `type` fuera de `{offer, answer, ice-candidate}` → el servidor cierra la conexión con código `4002` — el cliente debe validar el tipo de mensaje antes de enviarlo para no gatillar esto.

**Casos de Error**
- Corte de conexión → reconexión automática con backoff (1s→2s→4s→8s→30s máx.), banner de estado "Reconectando..." — esto sigue siendo válido, es responsabilidad del cliente WebSocket.
- Token JWT inválido o rol no autorizado para esa sala → el servidor cierra con código `4003` sin mensaje adicional — el frontend debe traducir ese código a un mensaje entendible ("No tienes acceso a esta consulta").
- Falta el token en la URL → cierre código `4001`.

**Lo que NO es implementable hoy (documentado, no diseñado como si funcionara):**
- Lista/agenda de teleconsultas (`/app/teleconsultas`) — sin `GET`.
- Cierre de sesión, guardado de diagnóstico, recomendación de IA post-consulta — sin endpoint.
- Notificación al paciente de que su teleconsulta está lista — sin backend de notificaciones (G7) y sin forma de que el paciente descubra el `room_token`.

---

## 3.8 M3 — Emergencia médica (Familiar/Paciente + Paramédico)

**Happy Path (Familiar/Paciente)**
1. Sistema detecta riesgo crítico (o el paciente reporta directo, `POST /api/emergencies/`, exclusivo del rol `patient`) → `/app/emergencias/:id` → **P-Emergencia-Activa**.
2. Ve guía de primeros auxilios paso a paso. ⚠️ **Corrección** ([00](00-alineacion-backend.md) §0.3 M1): el contenido es un **texto estático fijo** (`settings.MVP_FIRST_AID_GUIDE`), igual para cualquier paciente/triage — no hay generación real ni personalización. La API lo devuelve junto con la emergencia creada, sin ningún paso de espera intermedio (la respuesta del `POST` ya incluye la guía) — no debe mostrarse un estado de "generando guía", el contenido ya está disponible de inmediato.
3. Ve estado (`pending` → `dispatched`, único cambio de estado real que expone la API) — se traduce a "Ambulancia en camino" cuando pasa a `dispatched`.
4. *(No hay un tercer estado "atención en curso"/"cerrado" del lado de `Emergency` — ver §0.3 M4: el `status` "closed" nunca se produce por código; el cierre real ocurre en el `Caso` asociado, que el paciente puede ver reflejado indirectamente en `GET /api/cierre-caso/mis-casos/`.)*

**Happy Path (Paramédico)**
1. `/app/emergencias` (cola, `GET /api/emergencies/`, rol `nurse` incluido) → abre una → **P-Emergencia-Paramedico**: datos del paciente + guía (misma, estática) ya presentes en la respuesta.
2. `POST /api/emergencies/{id}/dispatch/` → cambia estado a `dispatched`.
3. ⚠️ **Se retira** "actualiza historial clínico desde el mismo detalle" ([00](00-alineacion-backend.md) §G12): `historial-interop-service` no tiene ningún endpoint de escritura. El paramédico puede **leer** el historial existente del paciente (`GET /historial/{patient_id}/`), no puede agregarle nada directamente — el historial solo se actualiza automáticamente cuando el caso se cierra (§3.9).

**Edge Cases**
- Varias personas con acceso a la misma emergencia (paciente + familiar, ambos con cuentas `patient` vinculadas al mismo `patient_id` si aplica) → todos ven el mismo estado consultando el mismo `GET /api/emergencies/{id}/` — no hay push en tiempo real (sin WebSocket de emergencias), por lo que cada cliente debe hacer polling.

**Casos de Error**
- `POST /dispatch/` sobre una emergencia que ya no está en `pending` → `400`, mensaje "Esta emergencia ya fue despachada".
- Paramédico sin conectividad → puede seguir leyendo la guía ya cargada (cachearla localmente al abrir la pantalla es responsabilidad del cliente); no puede despachar ni actualizar nada hasta reconectar, ya que no hay cola de escritura offline soportada por estos endpoints síncronos.

---

## 3.9 M3 — Cierre de caso (exclusivo del rol Profesional)

> ⚠️ **Corregido** ([00](00-alineacion-backend.md) §G9): `CierreCasoView` exige literalmente `rol == "professional"` — **ni `center_admin` ni `system_admin` pueden cerrar casos**, a diferencia del diseño original que lo permitía a ambos. El Administrador de Centro Médico conserva solo `GET .../verify/` (ver completitud sin poder cerrar). Además, un `Caso` solo existe hoy si se creó vía emergencia despachada (`emergency.dispatched` sí se consume) — la vía de teleconsulta está rota (§3.7, G3), así que en la práctica `/app/casos/:id/cierre` solo es alcanzable para casos que vienen de una emergencia.

**Happy Path**
1. `/app/casos/:id/cierre` (solo visible/accionable si `rol == "professional"`) → **P-Cierre-Caso**. La verificación real (`verify_case()`) exige únicamente 2 cosas — mucho más simple que un checklist multi-campo: (a) que `clinical_notes` no esté vacío, (b) que el caso tenga `teleconsult_id` o `emergency_id` (ya viene garantizado, porque el `Caso` no existe si no tiene al menos uno).
2. Profesional escribe sus notas clínicas → `POST /{id}/close/` con `{"clinical_notes": "..."}` → si pasa la verificación, `200` con el caso cerrado (se calcula `integrity_hash`, se marca `closed_at`) y se publica `caso.cerrado` → dispara consolidación de historial (M4, único evento que lo alimenta).

**Edge Cases**
- Notas vacías → el botón "Cerrar caso" permanece deshabilitado; el único campo que puede bloquear el cierre es `clinical_notes` (no hay más campos que verificar del lado del servidor).
- Un `professional` distinto al que atendió originalmente también puede cerrar el caso — no hay chequeo de que sea el mismo `professional_id` de la teleconsulta/emergencia.

**Casos de Error**
- `POST /close/` sobre un caso ya `closed` → `400`, "Este caso ya fue cerrado".
- Verificación falla (raro, dado que ambos requisitos ya están garantizados salvo notas vacías) → `409` con el detalle de `verify_case()` en la respuesta; el caso permanece abierto, las notas ya escritas no se pierden (persisten en el formulario del cliente hasta reintentar).

---

## 3.10 M4 — Consulta de historial clínico

> ⚠️ **Corregido** ([00](00-alineacion-backend.md) §G12, §0.3 M8): `historial-interop-service` es **de solo lectura** — no hay ningún endpoint de escritura manual. Además, el historial **solo acumula eventos de tipo `caso.cerrado`** (cada uno con `clinical_notes`, referencia a `teleconsult_id`/`emergency_id`, `integrity_hash`) — no hay entradas individuales de "solicitud creada" o "teleconsulta iniciada"; es una lista de casos cerrados, no un registro granular de cada paso clínico.

**Happy Path**
1. `/app/historial` (paciente, `GET /historial/{patient_id}/` con `patient_id == propio id`) o `/app/pacientes/:id/historial` (profesional/paramédico/center_admin, mismo endpoint) → **P-Historial**: lista/timeline de casos cerrados, cada uno con sus notas clínicas y el hash de integridad.
2. Usuario filtra por rango de fecha (client-side, sobre los eventos ya cargados — el endpoint no acepta query params de filtro).
3. Abre un evento (caso cerrado) específico para ver el detalle completo (`clinical_notes`, `teleconsult_id`/`emergency_id`, `closed_at`).

**Edge Cases**
- Paciente nuevo sin historial previo (ningún caso cerrado aún) → estado vacío explicativo, no una tabla en blanco (ver doc 11).

**Casos de Error**
- ⚠️ **Corregido**: el diseño original asumía `/403` si el profesional no tiene "relación de atención activa" con el paciente. **El backend real no verifica esto** (`can_read()` permite a cualquier `professional`/`nurse`/`center_admin` leer el historial de cualquier paciente — [00](00-alineacion-backend.md) §G10). No hay ningún caso de error de permisos entre roles clínicos hoy; solo un `patient` intentando ver el historial de otro `patient_id` distinto al propio recibe `403`. Este comportamiento más permisivo de lo esperado queda documentado como hallazgo de seguridad a escalar fuera del alcance de este paquete de UX (ver doc 14).

---

## 3.11 M4 — Administración: registro de centro médico (Admin SAMR)

> ⚠️ **Corregido** ([00](00-alineacion-backend.md) §G6): no existe `GET /centers/<id>/` ni listado con los 3 estados — solo `POST /centers/register/` (crear) y `GET /centers/available/` (solo los ya `validated`). La validación es automática e inmediata (Celery `.delay()`, resuelta por una variable de entorno fija, no una revisión real — ver §0.5), pero **no hay ninguna forma de consultar el resultado vía API**: un centro rechazado es completamente invisible; uno validado solo se confirma indirectamente si aparece más tarde en `/centers/available/`.

**Happy Path**
1. `/app/admin/centros/nuevo` → **P-Admin-Centro-Form**: formulario (nombre, tipo, ubicación, `license_number`, `specialties`) — nota: `license_number` y `specialties` viajan en el evento publicado pero **no se guardan** en la base de datos del centro (§0.3), solo `name/type/latitude/longitude/status` persisten.
2. Validación en tiempo real por campo en el cliente (el backend no tiene JSON Schema propio más allá de los tipos del serializer).
3. Envía (`POST /centers/register/`, exclusivo `system_admin` autenticado por JWT — un token de servicio M2M no puede usar esta ruta) → `201` inmediato con el centro en estado `pending_validation`.
4. *(Sin seguimiento posterior — ver brecha arriba.)* La pantalla debe comunicar honestamente que el resultado no es consultable todavía, en vez de simular un estado "pendiente" que nunca se resuelve visualmente.

**Edge Cases**
- Ninguno aplicable — sin `GET` de detalle no hay "borrador" recuperable ni estado intermedio que mostrar más allá de la confirmación de envío.

**Casos de Error**
- Error de validación de esquema (campos requeridos faltantes) → error inline por campo, envío bloqueado hasta corregir.
- ⚠️ Se retira "rechazo del Consorcio visible en el detalle, con opción de corregir y reenviar" — no hay detalle ni reenvío; si el admin sospecha un rechazo (el centro nunca aparece en disponibles), la única acción posible es **crear un nuevo registro**, no editar el anterior (no existe `PATCH`/`PUT` sobre `Center`).

---

## 3.12 M4 — Administración: registro de dispositivo IoT (Admin SAMR)

**Happy Path**
1. `/app/admin/dispositivos/nuevo` → **P-Admin-Dispositivo-Form**: paciente, tipo de dispositivo, número de serie.
2. Envía (`POST /devices/register/`) → `201` inmediato, dispositivo activo (`active=True` desde el inicio, sin validación posterior a diferencia de los centros) → evento `device.registered` habilita la ingesta de datos de ese `device_id` en `monitoring-service`.

**Edge Cases**
- Ninguno — sin `GET` de dispositivos, no hay forma de listar ni verificar duplicados desde el cliente antes de enviar.

**Casos de Error**
- Paciente no encontrado → ⚠️ el backend no valida que `patient_id` exista en `patient-service` (es un `UUIDField` suelto, sin verificación cruzada) — cualquier UUID con formato válido se acepta. El único control posible hoy es en el cliente (autocompletar buscando en `patient-service` antes de enviar), no una respuesta de error del servidor.
- ⚠️ Se retira "número de serie ya registrado → error con link al existente": `serial_number` se recibe en el formulario pero **no se persiste** en el modelo `Device` — no hay forma de que el backend detecte duplicados, ya que ese dato solo viaja en el evento publicado y se descarta después.

---

## 3.13 M4 — Auditoría de decisiones de IA (DPD)

> ⚠️ **Corregido** ([00](00-alineacion-backend.md) §0.3 M6/M7, M9): `GET /decisions/` no acepta ningún query param — devuelve los **100 registros más recientes sin filtrar**; cualquier filtro (fecha, módulo, nivel de riesgo) debe aplicarse **client-side** sobre esos 100. No hay `GET /decisions/<id>/` individual — el detalle sale de la misma lista ya cargada. El alcance real es más amplio de lo que sugiere el nombre del módulo: el consumidor se suscribe a **todos** los eventos del bus (`#`), no solo a decisiones de IA (incluye, por ejemplo, `auth.login_success`) — la UI debe poder mostrar tipos de evento no relacionados con IA sin romperse.

**Happy Path**
1. `/app/auditoria` → **P-Auditoria-Lista**: `GET /decisions/` (rol `dpd_delegate` exclusivo) trae los 100 más recientes; filtros de fecha/módulo/nivel de riesgo se aplican sobre ese conjunto ya en memoria del cliente — comunicar visualmente que el filtro opera "dentro de los últimos 100 registros", no sobre todo el histórico.
2. Abre una decisión (de la lista ya cargada, sin nueva llamada de red) → **P-Auditoria-Detalle**: `event_type`, `actor_id`, `payload`, `ai_confidence`, `ai_explainability`.
3. Marca estado de revisión: `PATCH /decisions/{audit_log_id}/review/` con `estado_revision` — **solo acepta `"revisado"` u `"observado"`**, no `"pendiente"` (es el default no seteable) ni `"rechazado"` (no existe ese estado).

**Edge Cases**
- Decisión sin metadatos de explicabilidad completos (`ai_confidence`/`ai_explainability` nulos — ocurre en eventos que no son de IA, ej. `auth.login_success`) → se muestra igual, con esos campos como "No aplica" en vez de vacíos confusos.
- Revisar un registro ya revisado → `update_or_create` **sobreescribe silenciosamente** la revisión anterior (sin historial de versiones) — la UI debe advertir "Ya existe una revisión de {revisor} el {fecha} — se reemplazará" antes de confirmar, ya que el backend no deja rastro de la anterior.

**Casos de Error**
- Intento de acceso sin rol `dpd_delegate` → `/403` inmediato, sin exponer ni el listado.
