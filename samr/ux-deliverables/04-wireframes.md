# 04 — Wireframes
## SAMR — Sistema de Atención Médica Remota

> Descripciones de layout, jerarquía visual, espaciado y propósito — no solo inventario de componentes. Todos los tokens de espaciado/color referenciados están definidos en el doc 05; los componentes en el doc 06. Grid base: contenedor `max-width: 1280px` centrado en desktop, columnas de 12 con `gap: space-6` (24px); en mobile, columna única con márgenes `space-4` (16px).

---

## 4.1 Convenciones generales de layout

- **Shell autenticado**: Navbar (64px fijo arriba) + Sidebar (260px fijo a la izquierda en desktop) + área de contenido con padding `space-6` (24px desktop) / `space-4` (16px mobile).
- **Header de página** (dentro del área de contenido, no confundir con Navbar): título `text-2xl` a la izquierda, acción primaria (botón) a la derecha, en la misma fila. Debajo, breadcrumb si aplica (doc 02 §2.7). Separación con el contenido: `space-6`.
- **Alineación**: todo el contenido de texto se alinea a la izquierda (nunca centrado, salvo pantallas de autenticación y estados vacíos/error, donde el foco es un único bloque central).

---

## 4.2 Autenticación

### P-Login
**Layout**: columna única centrada, `max-width: 400px`, verticalmente centrada en viewport completo (sin navbar/sidebar). Fondo con gradiente sutil (doc 05 §5.10).
**Jerarquía (arriba→abajo)**: logo SAMR (`space-8` de margen superior) → título "Inicia sesión" (`text-2xl`) → subtítulo breve (`text-sm` `gray-500`) → Input email/teléfono → Input contraseña (con toggle mostrar/ocultar) → link "¿Olvidaste tu contraseña?" alineado a la derecha bajo el input de contraseña → botón primario `lg` ancho completo "Iniciar sesión" → divisor "o" → link secundario "¿No tienes cuenta? Regístrate".
**Espaciado**: `space-4` entre cada input, `space-6` antes del botón primario.
**Propósito**: cero distracciones — un único camino de acción visible.

### P-Registro
**Layout**: igual base que Login pero `max-width: 480px`, formulario en una sola columna con secciones progresivas (no wizard de varios pasos — todo visible con scroll, dado que son pocos campos).
**Jerarquía**: título "Crea tu cuenta" → campos (nombre completo, email o teléfono, contraseña, confirmar contraseña) → sección de consentimientos LOPDP claramente separada visualmente (fondo `gray-50`, `radius-md`, padding `space-4`): checkbox obligatorio "Acepto el tratamiento de mis datos de salud" + checkbox obligatorio "Acepto el uso de IA para orientación clínica" + checkbox opcional "Acepto compartir mi expediente con MSP/IESS cuando aplique" → botón primario "Crear cuenta" (deshabilitado hasta que los 2 consentimientos obligatorios estén marcados, con tooltip explicando por qué) → link a Login.
**Propósito de la separación visual de consentimientos**: LOPDP exige consentimiento explícito e informado — no puede mezclarse visualmente con datos de perfil, debe leerse como una decisión distinta.

### P-RecuperarContrasena (3 sub-pantallas)
🔴 **Pendiente de backend** — ver [00](00-alineacion-backend.md) §G11. Mismo layout base de Login. Paso 1: input único (email/teléfono) + botón "Enviar instrucciones". Paso 2 (verificar): 6 casillas de un dígito cada una (input OTP) + botón "Reenviar código" (con cooldown, deshabilitado los primeros 30s). Paso 3 (nueva contraseña): input nueva contraseña + confirmar + indicador de fortaleza visual (barra de 3 segmentos, no solo texto). Se conserva la especificación completa para cuando `auth-service` agregue estos endpoints.

---

## 4.3 Dashboard (`/app/dashboard`) — varía 100% por rol

> ⚠️ **Corregido contra backend real** ([00](00-alineacion-backend.md) §G8): `bff-service` expone un único `GET /dashboard/` que siempre agrega las mismas 4 llamadas (`patient`, `evaluacion`, `monitoring`, `atencion`), sin distinguir rol. Para `patient` las 4 tienen sentido (aunque `monitoring` siempre falla, G1). Para cualquier otro rol, 2 o 3 de esos 4 bloques devolverán `{"error": ...}` porque esos endpoints están reservados a `patient`. **Recomendación aplicada aquí**: el frontend no debe usar el BFF para roles distintos de `patient` — debe llamar directamente a los endpoints de cada microservicio a través del gateway para armar el dashboard de cada rol. La tabla de abajo sigue siendo el diseño objetivo; la columna "Fuente de datos" indica de dónde sale cada bloque hoy.

**Layout base común**: grid de 12 columnas. Fila superior: saludo contextual ("Hola, María") + fecha, `text-xl`. Debajo, zona de **alertas/urgencia** (ancho completo, solo si hay algo que mostrar — nunca un espacio vacío reservado) → zona de **KPIs/resumen** (cards `card-stat`, 3-4 en fila desktop / 2 en tablet / 1 en mobile) → zona de **listas accionables** (2 columnas desktop: 8/12 + 4/12; 1 columna mobile).

| Rol | Zona de alerta | KPIs | Lista principal (8/12) | Panel lateral (4/12) | Fuente de datos |
|---|---|---|---|---|---|
| Paciente | Emergencia activa (`GET /api/emergencies/`) | — (no aplica KPIs a paciente) | ⚠️ Sin fuente — no hay listado de solicitudes (G2) | Accesos rápidos (Nueva solicitud, Ayuda) | BFF `/dashboard/` (bloques `patient`/`atencion` funcionan, `monitoring`/`evaluacion` no aportan nada útil al paciente) |
| Profesional | Casos críticos (client-side sobre la cola) | Casos en cola (conteo del array) | Cola de casos (`GET /mis-casos/`, global) | — (sin "agenda" real, sin `GET` de teleconsultas) | Directo al gateway, no BFF |
| Paramédico | Emergencia asignada activa | Emergencias hoy (conteo) | Cola de emergencias (`GET /api/emergencies/`) | — | Directo al gateway |
| Admin Centro | — (sin fuente, G13) | Casos visibles (conteo) | Casos (mismo endpoint global) | — | Directo al gateway |
| Admin SAMR | — | — (sin conteos: no hay listado de centros/dispositivos, G6) | Accesos rápidos (Nuevo centro, Nuevo dispositivo, Gestionar FAQ) | — | Sin datos agregables hoy — el dashboard de este rol es, en la práctica, un menú de accesos directos |
| DPD | Decisiones sin revisar (client-side sobre los 100 más recientes) | Revisadas vs. pendientes (conteo sobre esos 100) | Últimas decisiones sin revisar | — | Directo al gateway |

**Propósito de la regla "alerta primero"**: la jerarquía visual de urgencia (doc 05/09) manda sobre cualquier otro contenido del dashboard — si hay algo crítico, es lo primero que se ve, sin excepción, sin scroll.

---

## 4.4 M1 — Paciente/Familiar

### P-Chat-Solicitud (`/app/solicitudes/nueva`)
**Layout**: dos zonas verticales. Superior (70% alto): hilo de conversación estilo chat, mensajes del bot alineados a la izquierda (avatar del bot + burbuja `gray-100`), mensajes del usuario alineados a la derecha (burbuja `teal-600` texto blanco). Inferior (fija, 30%): input de texto + botón enviar + chips de respuestas rápidas sugeridas (cuando el bot ofrece opciones estructuradas) sobre el input.
**Jerarquía dentro de una burbuja de formulario embebido** (cuando el bot pide datos estructurados): título breve de la pregunta → campo(s) → botón "Continuar" dentro de la misma burbuja, no un modal separado — mantiene la sensación de conversación continua.
**Propósito**: nunca forzar al usuario a "salir" del chat a un formulario tradicional; los formularios estructurados viven dentro del flujo conversacional.

### P-Solicitud-Detalle (`/app/solicitudes/:id`)
> ⚠️ **Rediseñado contra backend real** ([00](00-alineacion-backend.md) §G2): `solicitud-service` no tiene `GET`. Este detalle solo puede poblarse con (a) la respuesta inmediata del `POST` que lo creó (disponible solo en esa misma sesión de navegación, se pierde al recargar) y (b) el resultado de `GET /api/evaluacion/riesgo/{solicitud_id}/` una vez evaluado.

**Layout**: header de contexto (paciente + fecha) → **stepper de estado reducido a 2 pasos reales** ("Enviada" ✓ siempre, y "Riesgo evaluado" que aparece solo cuando el polling a `/riesgo/` deja de dar 404) — los pasos intermedios ("Validando", "Evaluando") se muestran como un único estado combinado "En proceso" con mensaje contextual (doc 10), sin fingir granularidad que el backend no expone → debajo, tarjeta con el detalle de síntomas reportados (los mismos que el usuario envió, guardados en el cliente) → si `/riesgo/` ya respondió 200, badge de urgencia con `nivel_riesgo` en lenguaje simple.
**Propósito del stepper reducido**: comunicar exactamente lo que se puede verificar, ni más ni menos — un stepper de 5 pasos que en la práctica salta directo del 1 al 5 (o se queda colgado) es peor que uno honesto de 2 estados.

### P-Dispositivos — retirada del sitemap
🔴 Ver [00](00-alineacion-backend.md) §G1: `monitoring-service` excluye al rol `patient` de `GET /alerts/` (403), y no existe ningún endpoint de listado de dispositivos en ningún servicio. No hay ninguna combinación de llamadas que alimente esta pantalla hoy — se retira del wireframe (y del sitemap, doc 02) hasta que exista backend de lectura para el paciente.

---

## 4.5 M2 — Profesional de Salud

### P-Cola-Casos (`/app/casos`)
**Layout**: barra de filtros horizontal arriba (nivel de riesgo — como Chips removibles; ⚠️ filtro de "especialidad/estado" retirado, `Evaluacion` no tiene esos campos) → lista de Cards `card-urgencia` (ver doc 06.7), una por caso. `GET /mis-casos/` devuelve los 50 más recientes de todo el sistema sin ordenar por riesgo (ver [00](00-alineacion-backend.md) §0.3 M2) — **el ordenamiento por nivel de riesgo descendente se hace en el cliente**, después de recibir la respuesta. Cada card: borde izquierdo del color de urgencia + badge de nivel (ícono+color+texto) + `solicitud_id` (no hay nombre de paciente en `Evaluacion` — solo `patient_id`; mostrar nombre requiere una llamada adicional a `patient-service` por cada caso, evaluar si vale el costo o mostrar solo el ID) + tiempo transcurrido desde `created_at` + botón "Ver caso".
**Jerarquía**: el nivel de riesgo es el primer elemento visual (color + posición izquierda) — la priorización clínica sigue siendo la función principal de la pantalla, solo que ahora es responsabilidad del cliente, no una garantía del servidor.

### P-Detalle-Caso (`/app/casos/:id`)
**Layout**: dos columnas en desktop (8/12 + 4/12). Columna principal: header con datos del paciente y badge de riesgo grande → sección "Síntomas reportados" → sección "Datos biomédicos" (si vinieron en la solicitud original, sin gráfico de tendencia — el profesional no tiene acceso a `monitoring-service` desde aquí, sería una llamada aparte no contemplada) → sección "Evaluación de IA" con nivel de riesgo y `fuentes_rag` citadas — ⚠️ se retira "Ajustar nivel de riesgo": no existe ningún endpoint de actualización sobre `Evaluacion`, el valor es inmutable (ver [00](00-alineacion-backend.md) §0.3 M3). Columna lateral: única acción disponible "Iniciar matching" (se retira "Solicitar más información al paciente" — no hay ningún endpoint para eso) + timeline compacto del caso.
**Propósito de mostrar las fuentes RAG inline**: explicabilidad de IA a un clic — sigue siendo válido aunque hoy `fuentes_rag` sea siempre el mismo objeto fijo del simulador MVP (doc 00 §0.5); la UI debe mostrarlo igual, sin inventar variedad.

### P-Matching (`/app/casos/:id/matching`)
> ⚠️ **Rediseñado por completo** ([00](00-alineacion-backend.md) §G5): el backend no acepta `center_id` en la petición — no hay forma de que el profesional elija centro. `find_best_center()` decide automáticamente (primer centro disponible, orden alfabético) y el score es siempre `100.00` (constante).

**Layout**: pantalla de una sola acción, sin lista de candidatos. Card central con el resumen del caso (paciente, nivel de riesgo) + texto explicativo ("El sistema asignará automáticamente el centro médico disponible más adecuado") + botón primario único "Ejecutar matching". Al confirmar, llamada síncrona — no hay estado intermedio "confirmando disponibilidad" (era diseño previo asumiendo un paso asíncrono que no existe): la respuesta llega de inmediato como éxito (muestra el centro asignado por el sistema, recién conocido en ese momento) o como error "Sin centros disponibles" (409).
**Propósito del rediseño**: no simular una elección que el usuario no tiene — mostrar una lista de "candidatos" que en realidad no influyen en nada sería engañoso.

---

## 4.6 M3 — Atención

### P-Sala-Teleconsulta (`/app/teleconsultas/:id`)
> 🔴 **Brecha crítica** ([00](00-alineacion-backend.md) §G3/G4): esta pantalla (video/audio/texto vía WebSocket de señalización) sí funciona una vez que se tiene el `room_token`. Todo lo que ocurre *antes* (que el paciente lo reciba) y *después* (guardar diagnóstico, cerrar) no tiene backend — ver detalle abajo.

**Layout (Paciente)**: video a pantalla completa del profesional, thumbnail propio en esquina inferior derecha, barra de controles flotante (glassmorphism, doc 05 §5.9) centrada abajo: micrófono, cámara, chat de texto, colgar (en `error-600`, separado visualmente de los demás controles para evitar clics accidentales). Al colgar, ⚠️ **no hay pantalla de "resumen post-consulta"**: no hay ningún dato del servidor que resumir (sin diagnóstico guardado). Mostrar en su lugar un mensaje de cierre simple ("Consulta finalizada") sin prometer un resumen que no existe.
**Layout (Profesional)**: video ocupa 65% del ancho a la izquierda; panel lateral derecho (35%) con tabs (doc 06.8): "Notas clínicas" (⚠️ estas notas hoy solo pueden guardarse localmente en el cliente durante la llamada — no hay endpoint que las persista hasta que el caso se cierre por la vía de emergencia, si aplica) | "Asistencia IA" | "Historial del paciente" (lectura). Al "finalizar", **no hay botón de cierre real de la teleconsulta** — se retira el botón "Finalizar y cerrar caso" del diseño original; en su lugar, un botón "Salir de la llamada" que simplemente desconecta el WebSocket.
**Propósito del ajuste**: es preferible una interfaz honesta sobre lo que persiste (nada, hoy) a una que sugiere que el diagnóstico quedó guardado cuando no es así.

### P-Emergencia-Activa (`/app/emergencias/:id`, vista Paciente/Familiar)
**Layout**: pantalla de **máxima prioridad visual**, sin sidebar/navbar estándar (solo un header mínimo con estado de conexión). Fondo superior con el color de urgencia correspondiente (generalmente `crítico`, pulso 1Hz). Debajo: guía de primeros auxilios como lista numerada de pasos grandes (`text-lg`, un paso visible a la vez con navegación "Siguiente paso" — evita sobrecarga cognitiva bajo pánico). ⚠️ **Corrección** ([00](00-alineacion-backend.md) §0.3 M1): la guía llega completa en la misma respuesta que crea la emergencia — **no hay estado de carga que mostrar**, la pantalla debe renderizar el contenido de inmediato, sin skeleton ni mensaje "generando" (el contenido es estático, no se genera en tiempo real). → sección fija inferior con estado del despacho (traducción de `status`: `pending` = "Buscando ayuda", `dispatched` = "Ambulancia en camino" — sin ETA, la API no la provee, no inventar un minuto estimado) → botón de emergencia telefónica directa siempre visible (respaldo si algo en la app falla).
**Propósito de "un paso a la vez"**: bajo estrés agudo, una lista larga completa es más difícil de procesar que un paso claro con opción de avanzar — decisión de diseño explícita para el escenario de mayor carga emocional del sistema.

### P-Emergencia-Paramedico (`/app/emergencias/:id`, vista Paramédico)
**Layout mobile-first**: header con datos esenciales del paciente (nombre, edad — de `patient-service`, si el cliente decide llamarlo aparte; `Emergency` en sí solo trae `patient_id`/`triage_level`) siempre visible (sticky) → debajo, misma guía de primeros auxilios que ve el familiar (para estar alineados, y por ser el mismo contenido estático) → botón "Despachar" (`POST .../dispatch/`) si `status == pending`. ⚠️ Se retira el botón "Actualizar historial" ([00](00-alineacion-backend.md) §G12): no existe ningún endpoint de escritura en `historial-interop-service`. En su lugar, un link "Ver historial del paciente" (solo lectura) hacia `/app/pacientes/:id/historial`.

### P-Cierre-Caso (`/app/casos/:id/cierre`)
> ⚠️ **Ruta `/app/teleconsultas/:id/cierre` retirada** — no existe (G3). Esta pantalla solo es alcanzable para casos que vienen de una emergencia despachada, y **solo el rol `professional` la ve** (G9 — ni `center_admin` ni `system_admin` tienen el botón de cierre, solo `GET /verify/` de solo lectura).

**Layout**: formulario de una columna, `max-width: 640px`. Checklist de completitud simplificado a lo que el backend realmente verifica (`verify_case()`, [00](00-alineacion-backend.md) §0.3 M5): 2 ítems — "Notas clínicas completas" y "Origen de atención válido" (este último ya viene garantizado siempre en true, porque el `Caso` no se crea sin `emergency_id`/`teleconsult_id`) → campo de texto para `clinical_notes` (único campo real de entrada) → footer fijo con botón "Cerrar caso" (deshabilitado solo si `clinical_notes` está vacío).

---

## 4.7 M4 — Integración e Interoperabilidad

### P-Historial (`/app/historial`, `/app/pacientes/:id/historial`)
> ⚠️ **Ajustado** ([00](00-alineacion-backend.md) §0.3 M8): el historial solo contiene eventos `caso.cerrado` — es una lista de casos cerrados, no un registro granular por cada paso clínico. Se retira el filtro "tipo de evento" (solo hay un tipo).

**Layout**: header de contexto del paciente → filtro de rango de fecha (client-side, sobre los eventos ya cargados en el único `GET`) → Timeline vertical (doc 06.27) de casos cerrados, cada nodo con `closed_at`, un extracto de `clinical_notes` y el origen (emergencia/teleconsulta). Cada nodo expandible inline mostrando `clinical_notes` completas e `integrity_hash`.

### P-Admin-Centro-Form (`/app/admin/centros/nuevo`)
> ⚠️ **Se retiran `P-Admin-Centros-Lista` y `/:id`** ([00](00-alineacion-backend.md) §G6): no hay `GET` de listado ni de detalle. Solo queda el formulario de alta.

**Layout**: formulario de una sola sección (sin Accordion multi-sección con estados por seguir — no hay nada que "guardar como borrador" recuperable, ya que no hay persistencia parcial del lado del servidor): nombre, tipo, ubicación (lat/long), número de licencia, especialidades → botón único "Registrar centro". Al enviar, pantalla de confirmación explícita: "Centro enviado. La validación es automática — no podrás ver su estado desde aquí; aparecerá en el catálogo de centros disponibles si es aprobado." (honestidad sobre la brecha, en vez de simular un estado "pendiente" que nunca se resuelve visualmente).

### P-Admin-Dispositivo-Form (`/app/admin/dispositivos/nuevo`)
> ⚠️ **Se retira `P-Admin-Dispositivos-Lista`** (G6 — sin ningún `GET` de dispositivos).

**Layout**: formulario corto de una sección: buscar/seleccionar paciente (autocompletar contra `patient-service`, ya que el backend no valida que el `patient_id` exista — G6/§0.3), tipo de dispositivo, número de serie → botón "Registrar dispositivo". Confirmación de éxito simple (el dispositivo queda `active=True` de inmediato, sin validación posterior a diferencia de los centros).

### P-Admin-FAQ (`/app/admin/faq`) — NUEVA, soportada por backend
No estaba en la v1.0 de este paquete. `solicitud-service` expone `GET/POST/PATCH /api/solicitud/faq/`, exclusivo `system_admin` para escritura ([00](00-alineacion-backend.md) §0.4).
**Layout**: Tabla (doc 06.20) con columnas Pregunta / Respuesta (truncada) / Actualizada / Acciones (editar) → botón primario "Nueva pregunta" abre Modal con 2 campos (`question`, `answer`) → guardar hace `POST` (nueva) o `PATCH` (edición, el `id` va en el body, no en la URL — detalle de integración para el frontend, ver doc 12).

### P-Auditoria-Lista (`/app/auditoria`)
> ⚠️ **Ajustado** ([00](00-alineacion-backend.md) §0.3 M6): `GET /decisions/` no acepta query params — trae los 100 más recientes, sin más. Los filtros de la barra operan **sobre esos 100 registros ya cargados**, no sobre todo el histórico — un badge junto a la barra de filtros debe indicar "Filtrando dentro de los 100 registros más recientes" para no sugerir una búsqueda global inexistente.

**Layout**: barra de filtros (fecha, módulo/`event_type`, estado de revisión — todos client-side) → Tabla densa: Fecha, Tipo de evento, Nivel de confianza del modelo (si aplica — "No aplica" para eventos no-IA como `auth.login_success`, ver §0.3 M9), Estado de revisión (badge: solo `pendiente`/`revisado`/`observado`), Acción "Revisar".

### P-Auditoria-Detalle (`/app/auditoria/:id`)
**Layout**: dos columnas. Principal: `payload` de entrada, `ai_confidence`, `ai_explainability` — todo en secciones claramente rotuladas, formato de solo lectura tipo "ficha técnica". Lateral: formulario de revisión (estado: **solo `revisado`/`observado`, sin `rechazado`** — corregido de la v1.0) + comentario. ⚠️ Se retira "historial de revisiones previas": `update_or_create` sobreescribe sin dejar rastro — si ya existe una revisión, mostrar advertencia inline ("Ya revisado por {revisado_por} el {fecha} — guardar reemplazará esta revisión") en vez de un historial que el backend no guarda.

---

## 4.8 Transversales

### P-Notificaciones (`/app/notificaciones`)
🔴 **Pendiente de backend** ([00](00-alineacion-backend.md) §G7): `notification-service` no tiene ningún endpoint — solo loguea internamente. Se conserva la especificación completa como blueprint (es una expectativa básica del producto), pero no debe conectarse a datos simulados.
**Layout**: lista vertical de ítems, no tabla. Cada ítem: ícono según tipo + texto + timestamp relativo + punto indicador de no-leído (`teal-600`, desaparece al abrir). Notificaciones críticas (emergencia) se muestran con el mismo tratamiento visual del sistema de urgencia, ancladas arriba de la lista independientemente de la fecha.

### P-Perfil (`/app/perfil`)
> ⚠️ **Ajustado**: solo `patient-service` tiene un modelo de perfil extendido (`GET/PATCH /api/patients/me/`). Para los demás 5 roles, lo único disponible es `GET /api/auth/me/` (email, rol, fecha de creación) — sin nombre, sin datos adicionales de ningún tipo, porque `auth-service::User` no tiene esos campos.

**Layout (rol `patient`)**: columna única `max-width: 640px`. Avatar (iniciales, no hay campo de foto en ningún modelo) + email (de solo lectura, viene de `auth-service`) arriba → sección editable de datos clínicos básicos (tipo de sangre, alergias, condiciones crónicas — `PATCH /api/patients/me/`), marcada con nota de que es visible para profesionales que lo atiendan.
**Layout (otros roles)**: mismo esqueleto, drásticamente más corto — solo email y rol de solo lectura; sin sección editable, porque no hay ningún campo de perfil propio del rol en el backend.

### P-Configuracion (`/app/configuracion/*`)
**Layout**: Sidebar secundaria interna (tabs verticales: Seguridad, Privacidad, Accesibilidad — ⚠️ se retira el tab "Notificaciones" del menú, mueve a la pantalla `P-Notificaciones` misma como pendiente de backend, G7) + panel de contenido a la derecha. En mobile, se colapsa a Accordion (una sección expandida a la vez).
- **Seguridad**: ⚠️ **Ajustado** (G14): sin cambio de contraseña ni sesiones activas (no existen esos endpoints; el JWT es stateless). Único contenido real: botón "Cerrar sesión" (borra el token localmente) + texto explicativo de que la sesión expira automáticamente a los 15 minutos de inactividad (vida del `access_token`) y se renueva con el `refresh_token` mientras la app esté abierta.
- **Privacidad**: los 3 consentimientos LOPDP (datos, IA, compartición) como Switches individuales — **solo visible para el rol `patient`** (son campos de `Patient`, no existen para otros roles) — con descripción completa visible (no oculta en tooltip); `PATCH /api/patients/me/` al cambiar cualquiera.
- **Accesibilidad**: switches para "Aumentar tamaño de texto", "Reducir movimiento", "Alto contraste" — 100% local (no requiere backend, son preferencias de cliente) — con previsualización en vivo del efecto.

---

## 4.9 Patrones reutilizables

### Modales
Ver especificación de comportamiento en doc 06.25. Layout tipo: título → cuerpo (formulario o mensaje) → footer con acciones. **Modal de confirmación destructiva** (ej. cerrar caso, rechazar solicitud): ícono de advertencia + pregunta directa en `text-lg` + explicación de la consecuencia en `text-sm gray-600` + botones "Cancelar" (secondary, izquierda) / acción destructiva (derecha, requiere ese sea el botón con foco por defecto solo si la acción NO es destructiva — en destructivas, el foco por defecto es "Cancelar", para que un Enter accidental no ejecute la acción irreversible).

### Formularios
Un input por fila en formularios cortos (≤5 campos); grid de 2 columnas en formularios largos de uso profesional (admin), nunca en formularios dirigidos a paciente (siempre 1 columna, reduce carga cognitiva). Mensajes de error siempre debajo del campo, nunca solo como color de borde.

### Tablas
Ver doc 06.20. Encabezado de columna ordenable con ícono de flecha que aparece solo en hover/foco (no siempre visible, reduce ruido).

### Cards
Ver doc 06.7. Regla transversal: toda card clickeable tiene un único punto de entrada de foco (la card completa es el elemento tabbable, no botones anidados compitiendo), salvo que contenga una acción secundaria explícita (ej. menú `⋮`), en cuyo caso esa acción es su propio elemento tabbable independiente.

---

## 4.10 Estados visuales por pantalla (resumen — detalle completo en doc 11)

| Estado | Tratamiento visual general |
|---|---|
| **Vacío** | Ilustración line-art (doc 05 §5.8) centrada + título + descripción breve + acción primaria si aplica (ej. "Crear tu primera solicitud") |
| **Con datos** | Layout estándar descrito arriba por pantalla |
| **Cargando** | Skeleton Loader con la forma real del contenido (doc 06.29) — nunca spinner de página completa salvo en la primera carga del shell de autenticación |
| **Error** | Ilustración distinta a la de vacío (más neutra, sin tono negativo excesivo) + mensaje específico + acción de reintentar |
| **Sin conexión** | Banner persistente en la parte superior del contenido (no modal bloqueante) + funcionalidad degradada explícita |
| **Éxito** | Toast (doc 06.14) o, en flujos críticos completados (cierre de caso, registro de centro validado), una pantalla de confirmación breve con ícono de check grande antes de redirigir |
| **Permisos insuficientes** | Página `/403` completa (no un modal) — mensaje neutro, sin exponer qué existe detrás del permiso |
| **Mantenimiento** | Página `/mantenimiento` completa con tiempo estimado si se conoce |
