# 11 — Estados del Sistema
## SAMR — Sistema de Atención Médica Remota

> Los 8 estados obligatorios por pantalla: **Vacío · Con datos · Cargando · Error · Sin conexión · Éxito · Permisos insuficientes · Mantenimiento**. El tratamiento visual genérico de cada uno está en doc 04 §4.10; el copy exacto de vacíos/errores está en doc 10 §10.3/10.7. Este documento detalla las particularidades **por pantalla** donde el tratamiento genérico no basta — especialmente en los flujos de mayor consecuencia clínica.

---

## 11.1 Regla transversal de "Permisos insuficientes" y "Mantenimiento"

Estos dos estados **no se renderizan dentro de la pantalla** — son siempre una redirección a `/403` o `/mantenimiento` (páginas completas, doc 02/04). Por eso no se repiten en cada entrada de este documento; se documentan una sola vez aquí:

- **`/403`**: ilustración neutra + "No tienes permiso para ver esta información." + botón "Volver al dashboard". Nunca indica qué había detrás del permiso.
- **`/mantenimiento`**: ilustración neutra + "SAMR está en mantenimiento programado. Volvemos en {tiempo estimado}." + sin navegación disponible (todas las rutas redirigen aquí mientras el modo esté activo) salvo `/app/emergencias/*`, que **nunca** se bloquea por mantenimiento (ver §11.9 — la emergencia es la única superficie exenta del modo mantenimiento por diseño).

---

## 11.2 P-Solicitud-Detalle / P-Chat-Solicitud (M1 — Paciente)

> ⚠️ **Ajustado** ([00](00-alineacion-backend.md) §G2): no hay `GET` de solicitud — "Vacío" y "Con datos" no son estados de una carga de red, son estados de la sesión de navegación actual (si ya se envió una solicitud en esta sesión o no).

| Estado | Tratamiento específico |
|---|---|
| Vacío | "Aún no has enviado ninguna solicitud en esta sesión" — no "no tienes solicitudes" (no hay forma de saber si tuvo alguna antes) |
| Con datos | Stepper reducido a 2 pasos reales + detalle de lo que el propio `POST` devolvió (doc 04 §4.4) |
| Cargando | Skeleton solo durante el `POST` inicial y durante el polling a `/riesgo/`; no hay una "carga de detalle" real que skeletonizar más allá de eso |
| Error | "No pudimos enviar tu solicitud" + reintentar; el chat en curso nunca pierde el borrador (persistencia local) |
| Sin conexión | Banner superior "Sin conexión — tu mensaje se enviará cuando vuelvas a estar en línea", el input del chat sigue aceptando texto (cola local) |
| Éxito | Toast "Solicitud enviada" al completar el paso 5 del flujo (doc 03 §3.4) |

## 11.3 P-Cola-Casos / P-Detalle-Caso (M2 — Profesional)

| Estado | Tratamiento específico |
|---|---|
| Vacío | "No hay casos pendientes ahora mismo" — tono neutro-positivo, no genera ansiedad de "algo está roto" |
| Con datos | Lista priorizada por riesgo (doc 04 §4.5) |
| Cargando | Skeleton de 3 cards con la forma exacta de `card-urgencia` (badge + título + meta) |
| Error | "No pudimos cargar la cola de casos" — este error tiene prioridad de reintento automático inmediato (sin esperar acción del usuario) dado el riesgo clínico de no ver casos activos |
| Sin conexión | Banner superior persistente + la cola muestra el último estado conocido con timestamp "Última actualización: hace {n} min" — nunca una pantalla en blanco |
| Éxito | Sin toast al cargar (no es una acción del usuario); sí toast al confirmar una acción (ej. "Nivel de riesgo actualizado") |

## 11.4 P-Matching (M2)

> ⚠️ **Ajustado** ([00](00-alineacion-backend.md) §G5): es una acción de un solo paso síncrona, no un listado con su propio ciclo de carga.

| Estado | Tratamiento específico |
|---|---|
| Con datos | Pantalla de una sola acción (botón "Ejecutar matching", doc 04 §4.5) |
| Cargando | El botón entra en estado `loading` (doc 06.1) durante la llamada síncrona — sin skeleton de lista, no hay candidatos que precargar |
| Error (409, sin centro disponible) | "No hay centros disponibles en este momento" + botón "Reintentar más tarde" — sin reintento automático ni sugerencia de siguiente candidato (no existen) |
| Error (400, ya tiene matching) | "Este caso ya tiene recursos asignados" — estado terminal, sin acción de reintento |
| Sin conexión | Botón de matching deshabilitado con aviso explícito — es una acción que compromete un recurso real, no debe encolarse para ejecutar después sin que el profesional lo confirme de nuevo con conexión activa |

## 11.5 P-Sala-Teleconsulta (M3)

> ⚠️ **Ajustado** ([00](00-alineacion-backend.md) §G3/G4): no hay servidor que confirme "sesión válida" más allá de que el WebSocket acepte la conexión — no hay estado "vacío" ni "éxito con resumen", porque no hay backend detrás de esos conceptos.

| Estado | Tratamiento específico |
|---|---|
| Con datos | Layout de doc 04 §4.6 |
| Cargando | Pantalla de pre-chequeo de cámara/micrófono mientras se establece la conexión WebSocket — nunca un spinner sobre fondo negro |
| Error | Cierre de WebSocket con código `4001` (falta token) / `4003` (token inválido o rol no autorizado para esa sala) → traducir a "No pudimos conectarte a esta consulta" — no exponer el código numérico al usuario final |
| Error (dispositivo) | "No pudimos conectar tu {cámara/micrófono}" con guía de solución (doc 10 §10.3) — comportamiento 100% de cliente, no depende del backend |
| Sin conexión | Reconexión automática con backoff exponencial (doc 03 §3.7, doc 08); banner "Reconectando…" visible a ambas partes; tras 3 intentos, banner con número de teléfono de respaldo del centro |
| Éxito | ⚠️ Se retira "pantalla de resumen post-consulta con diagnóstico" — no hay ningún dato del servidor que resumir. Al salir, mensaje simple "Consulta finalizada" sin prometer un resumen persistido. |

## 11.6 P-Emergencia-Activa / P-Emergencia-Paramedico (M3 — máxima criticidad)

| Estado | Tratamiento específico |
|---|---|
| Vacío | No aplica — esta ruta solo existe cuando hay una emergencia real |
| Con datos | Layout de doc 04 §4.6, guía paso a paso |
| Cargando | ⚠️ **Corregido** ([00](00-alineacion-backend.md) §0.3 M1): la guía es un texto estático que llega en la misma respuesta que crea la emergencia — no hay una fase de "generación" que comunicar. El único loading real es la creación de la `Emergency` en sí (típicamente instantánea); no mostrar mensajes de "preparando instrucciones" que sugieran personalización inexistente |
| Error | Si falla la creación de la emergencia en sí (no la guía, que no se "genera" por separado) → reintento inmediato automático + el botón de llamada de emergencia se vuelve más prominente como respaldo |
| Sin conexión | **Esta es la única pantalla donde "sin conexión" no degrada funcionalidad silenciosamente**: la guía ya descargada permanece visible offline (cacheada al recibir la alerta), y se muestra "Sin conexión — mostrando la última guía recibida" — el botón de llamada telefónica de respaldo funciona incluso sin datos móviles (llamada de voz estándar) |
| Éxito | ⚠️ **Corregido**: `Emergency.status` solo transiciona `pending → dispatched` — no existe un tercer estado alcanzable de "en curso"/"cerrado" en este servicio (ver [00](00-alineacion-backend.md) §0.3 M4). Al pasar a `dispatched`, actualizar el banner de estado sin prometer una "pantalla de cierre" automática — el cierre real ocurre en `Caso` (§3.9), como una acción separada del profesional |

## 11.7 P-Cierre-Caso (M3 — solo rol `professional`, [00](00-alineacion-backend.md) §G9)

| Estado | Tratamiento específico |
|---|---|
| Con datos | Checklist simplificado a 2 ítems reales (doc 04 §4.6) |
| Error | Si `clinical_notes` está vacío, botón deshabilitado (no llega a llamar al servidor); si `verify_case()` falla igual (caso límite), 409 con el detalle — el caso permanece abierto, notas ya escritas nunca se pierden (autoguardado local antes de cualquier intento de cierre) |
| Éxito | Pantalla de confirmación breve con ícono de check grande antes de redirigir (doc 04 §4.10) — no un simple toast, dado que es una acción irreversible |
| Permisos insuficientes | Para `center_admin`/`system_admin`/cualquier rol distinto a `professional`, el botón de cierre ni siquiera se renderiza (no es un 403 al hacer clic — se oculta la acción por RBAC de UI, coherente con el 403 real del backend) |

## 11.8 P-Historial (M4)

| Estado | Tratamiento específico |
|---|---|
| Vacío | "Todavía no hay eventos en este expediente" (doc 10 §10.7) |
| Cargando | Skeleton de Timeline (nodos + líneas grises en la forma real) |
| Error | "No pudimos cargar el historial" + reintentar; nunca se muestra un historial parcial sin indicarlo explícitamente ("Mostrando información parcial — algunos eventos podrían no estar disponibles") |
| Sin conexión | Muestra el historial cacheado localmente (si existe) con aviso de que puede no estar actualizado |

## 11.9 P-Admin-Centro-Form / P-Admin-Dispositivo-Form (M4)

> ⚠️ **Corregido** ([00](00-alineacion-backend.md) §G6): sin listado ni detalle, no hay estados "Vacío"/"Cargando"/"Error" de una tabla que ya no existe en el sitemap — solo quedan los estados del formulario de alta en sí.

| Estado | Tratamiento específico |
|---|---|
| Con datos (formulario) | Formulario de una sección (doc 04 §4.7) |
| Error | Error de validación de esquema → inline por campo, envío bloqueado |
| Éxito | Pantalla de confirmación explícita indicando que no hay seguimiento posterior disponible (doc 10 §10.3, fila "Confirmación de envío de centro") — no un simple toast que sugiera que el proceso "ya terminó" cuando en realidad la validación sigue corriendo de forma invisible |

## 11.10 P-Auditoria-Lista / P-Auditoria-Detalle (M4 — DPD)

| Estado | Tratamiento específico |
|---|---|
| Vacío (sin filtro) | No aplica en operación normal (siempre hay decisiones de IA registradas); si ocurre, mensaje neutro sin alarmar ("Aún no hay decisiones registradas") |
| Vacío (con filtro) | "No encontramos decisiones con esos filtros **dentro de los 100 registros más recientes**" + "Limpiar filtros" (doc 10 §10.7) — aclarar el alcance limitado del filtro (ver [00](00-alineacion-backend.md) §0.3 M6), ya que no es una búsqueda contra todo el histórico |
| Error | "No pudimos cargar el registro de auditoría" — dado que es un requisito de cumplimiento regulatorio, este error incluye un identificador de incidente visible para que el DPD pueda reportarlo formalmente si persiste |
| Revisión sobre un registro ya revisado | No es un error, pero requiere confirmación: "Ya revisado por {revisado_por} — guardar reemplazará esa revisión" antes de confirmar (`update_or_create` no deja historial, [00](00-alineacion-backend.md) §0.3 M7) |

## 11.11 Notificaciones, Perfil, Configuración (transversales)

| Estado | Tratamiento específico |
|---|---|
| Notificaciones — todos los estados | 🔴 Pendiente de backend en su totalidad ([00](00-alineacion-backend.md) §G7) — no implementar contra datos simulados |
| Perfil — Vacío/Con datos | Solo aplica contenido editable para rol `patient`; otros roles solo ven email/rol de solo lectura (doc 04 §4.8) |
| Cargando | Skeleton de lista/formulario simple |
| Error | Mensaje genérico + reintentar — baja criticidad, no requiere tratamiento especial |
| Éxito | Toast simple al guardar cambios de perfil/configuración |

## 11.12 Estado global "Sin conexión" — banner del sistema

Definido una sola vez porque su comportamiento es transversal (Navbar, doc 02 §2.6): aparece tras **3 intentos fallidos** de reconexión (umbral definido en la arquitectura v4, backoff 1s→2s→4s→8s→30s). Texto: "Sin conexión — reintentando automáticamente." Desaparece con fade-out (doc 08) apenas se restablece la conexión, sin requerir acción del usuario. Nunca bloquea la interfaz salvo en las acciones explícitamente marcadas como no-seguras-offline (§11.4, confirmación de matching).

## 11.13 Resumen — matriz de excepciones (pantallas con tratamiento no-genérico)

| Pantalla | Excepción respecto al patrón genérico (doc 04 §4.10) |
|---|---|
| Emergencia activa | Guía offline cacheada permanece funcional; contenido estático sin fase de "generación"; exenta de modo mantenimiento |
| Cola de casos | Reintento automático inmediato en error (no espera acción del usuario) |
| Matching | Acción síncrona de un solo paso; deshabilitada (no encolada) en offline |
| Teleconsulta | Sin "éxito con resumen" — no hay backend que lo respalde (G3) |
| Cierre de caso | Éxito = pantalla completa, no toast, por ser acción irreversible; acción oculta por RBAC de UI para roles distintos a `professional` |
| Admin Centro/Dispositivo | Sin estados de listado — solo formulario de alta y confirmación de envío sin seguimiento (G6) |
| Auditoría | Error incluye identificador de incidente; filtros aclaran su alcance limitado a 100 registros; advertencia al sobreescribir una revisión |
| Notificaciones | Toda la pantalla pendiente de backend (G7) |
