# 10 — UX Writing
## SAMR — Sistema de Atención Médica Remota

> Idioma base: **español** (el sistema soporta ES/EN vía i18next, arquitectura v4 — este copy deck es la fuente `es.json`; la traducción a `en.json` se deriva de este documento, no al revés). Todo el copy dirigido a paciente/familiar evita jerga médica y tecnicismos de sistema ("token", "endpoint", "payload" nunca llegan al usuario).

---

## 10.1 Voz y tono

| Principio | Qué significa en SAMR |
|---|---|
| **Claro antes que formal** | "No pudimos guardar tu solicitud" en vez de "Se ha producido un error en el procesamiento de la solicitud" |
| **Calmado, nunca alarmista fuera de lugar** | El tono se reserva la urgencia real para cuando realmente hay urgencia — un error de red no suena igual que una alerta crítica |
| **Directo, sin diminutivos infantilizantes** | Nunca "¡Uy, algo salió mal!" — trata al usuario como adulto, incluso en un error |
| **Instructivo, no solo descriptivo** | Todo mensaje de error indica qué hacer, no solo qué pasó |
| **Consistente en persona gramatical** | Siempre segunda persona singular ("tu solicitud", "puedes reintentar") — nunca mezcla con "usted" ni con tercera persona impersonal |

---

## 10.2 Botones (copy exacto)

| Contexto | Texto del botón |
|---|---|
| Enviar formulario de login | Iniciar sesión |
| Enviar registro | Crear cuenta |
| Enviar recuperación | Enviar instrucciones |
| Reenviar código OTP | Reenviar código |
| Enviar nueva solicitud | Enviar solicitud |
| Continuar en chat (dato estructurado) | Continuar |
| Confirmar asignación de recurso | Asignar |
| Iniciar teleconsulta | Iniciar teleconsulta |
| Unirse a teleconsulta (paciente) | Unirme a la consulta |
| Colgar / salir de teleconsulta | Salir |
| Cerrar caso (irreversible) | Cerrar caso |
| Cancelar en modal de confirmación | Cancelar |
| Confirmar acción destructiva | Sí, cerrar caso / Sí, rechazar |
| Guardar borrador | Guardar borrador |
| Enviar a validación (admin) | Enviar a validación |
| Reintentar tras error | Reintentar |
| Botón de emergencia telefónica | Llamar a emergencias |
| Cerrar sesión | Cerrar sesión |

---

## 10.3 Mensajes de error (por escenario)

| Escenario | Mensaje |
|---|---|
| Credenciales incorrectas | Correo o contraseña incorrectos. Verifica e intenta de nuevo. |
| Cuenta bloqueada (5 intentos) | Tu cuenta está bloqueada temporalmente por seguridad. Podrás intentarlo de nuevo en {tiempo}. |
| Email ya registrado | Ya existe una cuenta con este correo. ¿Quieres iniciar sesión? |
| Contraseña no cumple política | La contraseña debe tener al menos 8 caracteres, con letras y números. |
| Falla de red genérica | No pudimos conectar. Tus datos no se perdieron — intenta de nuevo. |
| Timeout de orientación del bot | Esto está tardando más de lo normal. Puedes seguir esperando o continuar sin orientación previa. |
| Validación de solicitud pendiente/reintento | Estamos validando tu solicitud, está tomando un poco más de tiempo de lo usual. No necesitas hacer nada. |
| Solicitud rechazada por datos incompletos | Tu solicitud necesita {campo faltante} para continuar. |
| Sin centros disponibles al ejecutar matching (mensaje real, sin reintento automático — ver [00](00-alineacion-backend.md) §G5) | No hay centros disponibles en este momento. Puedes intentarlo de nuevo en unos minutos. |
| Corte de conexión en teleconsulta | Reconectando… |
| Reconexión fallida tras 3 intentos | Perdimos la conexión. Puedes llamar directamente a {teléfono del centro} mientras lo resolvemos. |
| Falla de cámara/micrófono | No detectamos tu {cámara/micrófono}. Revisa los permisos del navegador e intenta de nuevo. |
| Alerta de emergencia no entregada tras reintentos | No pudimos confirmar que la alerta llegó. Estamos intentando por otro medio. |
| Cierre de caso con datos incompletos | Completa {campo} antes de cerrar este caso. |
| Confirmación de envío de centro (no hay forma de saber el resultado — ver [00](00-alineacion-backend.md) §G6) | Centro enviado para validación. La revisión es automática; si es aprobado, aparecerá en el catálogo de centros disponibles. |
| Acceso sin permisos (403) | No tienes permiso para ver esta información. |
| Página no encontrada (404) | No encontramos lo que buscabas. |
| Error de servidor (500) | Algo falló de nuestro lado. Ya lo estamos revisando — intenta de nuevo en unos minutos. |
| Modo mantenimiento | SAMR está en mantenimiento programado. Volvemos en {tiempo estimado}. |

---

## 10.4 Confirmaciones

| Escenario | Título | Descripción | Botón primario |
|---|---|---|---|
| Cerrar caso | ¿Cerrar este caso? | Esta acción no se puede deshacer. El expediente se consolidará en el historial clínico del paciente. | Sí, cerrar caso |
| Rechazar solicitud | ¿Rechazar esta solicitud? | El paciente será notificado del motivo que indiques. | Sí, rechazar |
| Revocar consentimiento (privacidad) | ¿Retirar este consentimiento? | Podrías perder acceso a funciones que dependen de él, como la orientación por IA. | Sí, retirar |
| Eliminar conversación (derecho al olvido) | ¿Eliminar esta conversación? | Se eliminará de forma permanente y no podrá recuperarse. | Sí, eliminar |
| Salir de teleconsulta en curso | ¿Salir de la consulta? | Aún estás en sesión con tu profesional de salud. | Sí, salir |
| Cerrar sesión | ¿Cerrar sesión? | — | Sí, cerrar sesión |

---

## 10.5 Tooltips

| Elemento | Texto |
|---|---|
| Botón deshabilitado por checklist incompleto | Completa {campo pendiente} para continuar |
| Ícono de fuente RAG | Evidencia clínica usada por la IA para esta evaluación |
| Ícono de nivel de confianza del modelo | Qué tan segura está la IA de este resultado |
| Botón "Ajustar nivel de riesgo" | Puedes corregir el nivel calculado por la IA con tu criterio clínico |
| Indicador de conexión degradada | Tu conexión es inestable — algunas funciones pueden tardar más |
| Botón colapsar sidebar | Contraer menú |
| Switch de accesibilidad | Cambios visibles de inmediato en tu pantalla |

---

## 10.6 Placeholders

| Campo | Placeholder |
|---|---|
| Email/teléfono (login) | tu@correo.com o número de teléfono |
| Contraseña | Mínimo 8 caracteres |
| Chat de solicitud | Cuéntanos qué síntomas tienes… |
| Búsqueda de casos | Buscar por paciente o síntoma |
| Comentario de auditoría | Agrega una observación (opcional) |
| Motivo de rechazo | Explica brevemente por qué se rechaza |

**Regla**: ningún placeholder reemplaza a un `<label>` visible (doc 09 §9.9) — siempre es información complementaria, nunca la única identificación del campo.

---

## 10.7 Empty states (copy)

| Pantalla | Título | Descripción | Acción |
|---|---|---|---|
| `/app/solicitudes` sin solicitudes previas | Aún no tienes solicitudes | Cuando reportes un síntoma, aparecerá aquí con su estado en tiempo real. | Crear mi primera solicitud |
| `/app/dispositivos` sin dispositivos vinculados | No tienes dispositivos vinculados | Un administrador de tu centro médico puede vincular un dispositivo de monitoreo a tu perfil. | — |
| `/app/casos` sin casos en cola | No hay casos pendientes ahora mismo | Los nuevos casos aparecerán aquí, priorizados por nivel de riesgo. | — |
| `/app/historial` sin eventos | Todavía no hay eventos en este expediente | El historial se completa automáticamente con cada atención. | — |
| `/app/notificaciones` sin notificaciones | Estás al día | No tienes notificaciones nuevas. | — |
| `/app/admin/centros` sin centros | Aún no hay centros registrados | Registra el primer centro médico del consorcio. | Registrar centro |
| `/app/auditoria` sin resultados de filtro | No encontramos decisiones con esos filtros | Prueba ajustando el rango de fecha o el nivel de riesgo. | Limpiar filtros |

---

## 10.8 Onboarding

**Primer ingreso — Paciente** (tooltip guiado breve, máximo 3 pasos, siempre descartable):
1. "Aquí puedes contarnos qué síntomas tienes, cuando quieras." → señala "Nueva solicitud".
2. "Te avisaremos aquí en cada paso de tu solicitud." → señala Notificaciones.
3. "Si algo es urgente, lo verás resaltado de inmediato — no tienes que buscarlo." → señala zona de alerta del dashboard.

**Primer ingreso — Profesional de Salud**:
1. "Tus casos aparecen priorizados por nivel de riesgo, no por orden de llegada." → señala cola de casos.
2. "Cada evaluación de IA muestra su evidencia — un clic y la ves." → señala sección de fuentes RAG.

**Primer ingreso — Administrador SAMR / DPD**: sin onboarding guiado — son roles de uso profesional recurrente, se asume capacitación previa fuera del producto; solo tooltips contextuales bajo demanda (ícono "?" junto a términos técnicos como "validación M2M").

---

## 10.9 Notificaciones (push / in-app)

🔴 **Pendiente de backend en su totalidad** ([00](00-alineacion-backend.md) §G7) — `notification-service` no entrega nada a un cliente hoy (solo loguea internamente). Este copy se conserva como especificación lista para cuando exista push/WebSocket real.

| Evento | Texto |
|---|---|
| Solicitud validada | Tu solicitud fue validada y ya está en evaluación. |
| Riesgo evaluado (no crítico) | Ya evaluamos tu caso. Nivel de riesgo: {nivel}. |
| Escalamiento a caso prioritario | Tu caso fue priorizado para atención inmediata. |
| Recursos asignados | Tienes una teleconsulta asignada con {profesional} a las {hora}. |
| Emergencia — anomalía detectada | Detectamos una posible anomalía en tus signos vitales y ya iniciamos una solicitud. |
| Emergencia — alerta crítica | **Emergencia detectada.** Abre la app ahora para ver qué hacer. |
| Ambulancia despachada | Una ambulancia va en camino. Llegada estimada: {tiempo}. |
| Teleconsulta por comenzar | Tu teleconsulta empieza en 5 minutos. |
| Caso cerrado | Tu atención fue registrada. Puedes ver el resumen aquí. |
| Centro médico validado (admin) | El centro {nombre} fue validado y ya está activo. |
| Centro médico rechazado (admin) | El centro {nombre} fue rechazado: {motivo}. |
| Decisión de IA pendiente de revisión (DPD) | Tienes {n} decisiones de IA nuevas por revisar. |

---

## 10.10 Guía de primeros auxilios — estilo de escritura

Cada paso: **verbo en imperativo, una sola acción, máximo 15 palabras.**

Ejemplo (referencial, el contenido clínico real lo genera el RAG/LLM, pero debe respetar este formato):
- ✅ "Recuesta a la persona boca arriba."
- ✅ "Llama en voz alta para verificar si responde."
- ❌ "Es importante que en este momento usted proceda a recostar cuidadosamente a la persona afectada boca arriba, verificando su respuesta."

---

## 10.11 Copy de consentimientos LOPDP (registro y configuración de privacidad)

| Consentimiento | Texto completo (no resumido, ni siquiera en el checkbox) |
|---|---|
| Tratamiento de datos | Acepto que SAMR trate mis datos de salud para brindarme orientación y atención médica remota, conforme a la Ley Orgánica de Protección de Datos Personales del Ecuador. |
| Uso de IA | Acepto que SAMR use inteligencia artificial (LLM/RAG) para orientarme y evaluar el riesgo de mis síntomas. Un profesional de salud siempre puede revisar y corregir estas evaluaciones. |
| Compartición interinstitucional (opcional) | Acepto compartir mi expediente clínico con el MSP y/o el IESS cuando corresponda a mi atención, para dar continuidad a mi cuidado entre instituciones. |

---

## 10.12 Estados de carga (microcopy, no solo skeleton visual)

> ⚠️ **Ajustado contra backend real** ([00](00-alineacion-backend.md) §0.5): la fila "Generando guía de primeros auxilios" se retira — el contenido es estático y llega en la misma respuesta que crea la emergencia, no hay espera real que comunicar (mostrar el contenido de inmediato, sin este mensaje). Las filas de "Validando con el Consorcio" y "Buscando centros" describen un estado que existe en la base de datos pero que hoy no es consultable por el frontend (§G2/§G6) — se conservan como especificación para cuando exista el endpoint, no para conectarse a un mock.

| Contexto | Texto contextual (acompaña al Skeleton, doc 06.29) |
|---|---|
| Evaluando riesgo (polling a `GET /riesgo/`) | Evaluando el nivel de urgencia de tus síntomas… |
| Ejecutando matching (llamada síncrona, breve) | Asignando el centro médico más adecuado para tu caso… |
| Validando con el Consorcio 🔴 pendiente de backend (G2) | Validando tu solicitud con la red de centros médicos… |
| Cargando historial | Cargando tu expediente clínico… |
