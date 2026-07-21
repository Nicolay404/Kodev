# 14 — Recomendaciones UX
## SAMR — Sistema de Atención Médica Remota

> Recomendaciones que van más allá de la especificación base — mejoras priorizadas por impacto en usabilidad, conversión (finalización de flujos), claridad, accesibilidad, rendimiento percibido y experiencia general. No son parte del alcance mínimo del doc 13, son propuestas de valor agregado a evaluar con el equipo de producto.
>
> **v1.1**: se agrega la sección **14.0**, de una naturaleza distinta a las demás — no son mejoras sobre un backend funcional, son **brechas que bloquean** que el diseño ya especificado (docs 02–04) funcione de punta a punta. Deben resolverse antes o en paralelo al desarrollo de frontend, no después.

---

## 14.0 Brechas críticas de backend (bloquean el diseño ya especificado)

> Cada ítem cita su entrada completa en [00 — Alineación con el Backend Real](00-alineacion-backend.md). Priorizadas por cuánto del producto dejan inutilizable, no por facilidad de implementación.

| Prioridad | Brecha | Qué desbloquea | Ref. |
|---|---|---|---|
| 🔴 **Máxima** | Cerrar teleconsultas: `POST` de cierre, guardado de `diagnosis`, y publicar `teleconsult.closed` | Todo el módulo M3 no-emergencia — hoy una teleconsulta iniciada no puede terminar formalmente ni generar historial | G3 |
| 🔴 **Máxima** | Forma de que el paciente descubra el `room_token` de su teleconsulta (endpoint `GET /api/teleconsult/mis-sesiones/` o equivalente) | El paciente pueda siquiera unirse a la videollamada que el profesional creó para él | G4 |
| 🔴 Alta | `GET` de solicitud (lista + detalle) en `solicitud-service` | Que el paciente vea el estado real de lo que reportó — hoy es una caja negra tras el envío | G2 |
| 🔴 Alta | Backend real de notificaciones (push o WebSocket, con endpoint de listado) | Cualquier forma de avisar proactivamente a un usuario — hoy nada llega salvo que la persona vuelva a abrir la app y consulte manualmente | G7 |
| 🔴 Alta | Recuperación de contraseña completa en `auth-service` | Requisito básico de cualquier producto con login — hoy un usuario bloqueado fuera de su cuenta no tiene salida | G11 |
| 🟠 Media-alta | `GET` de listado y detalle de centros médicos (con sus 3 estados) en `admin-integracion-service` | Que el Administrador SAMR pueda auditar su propio catálogo — hoy un rechazo es invisible | G6 |
| 🟠 Media-alta | API de disponibilidad de profesionales/camas/servicios por centro | El rol Administrador de Centro Médico prácticamente no tiene funcionalidad propia sin esto (doc 02, sidebar muy reducido) | G13 |
| 🟠 Media | Endpoint de escritura en `historial-interop-service` para notas de campo | Que un paramédico/profesional pueda registrar algo fuera del cierre formal de un caso | G12 |
| 🟡 Media-baja | `center_id` opcional en `POST /matching/` para permitir selección manual cuando el profesional lo necesite | Recupera el control clínico que el diseño original asumía (elegir centro, no solo aceptar el auto-asignado) | G5 |
| 🟡 Media-baja | Filtros server-side (fecha, tipo, rol) en `GET /decisions/` de `audit-service`, con paginación real | Que la auditoría escale más allá de "los últimos 100" a medida que crece el volumen de decisiones de IA | §0.3 M6 |
| 🟢 Baja (endurecimiento, no bloqueo) | `REVOKE UPDATE/DELETE` a nivel de base de datos sobre `audit_log`, no solo guarda de aplicación | Cumple la promesa de inmutabilidad "a nivel de motor" que la arquitectura v4 declara | §0.3 M10 |
| 🟢 Baja (seguridad, fuera de alcance UX) | Verificar relación de cuidado antes de permitir lectura de historial clínico por un profesional | Cierra una brecha de control de acceso — a escalar al equipo de seguridad, no es una decisión de diseño de interfaz | G10 |

**Cómo usar esta tabla**: no es una lista de "features bonitas a futuro" — cada fila es la razón concreta por la que una pantalla ya diseñada en los docs 02–04 quedó marcada 🔴 o 🟡. Resolver las dos de prioridad máxima (G3, G4) desbloquea, por sí solo, la mitad del módulo de Atención.

---

## 14.1 Usabilidad

1. **Autocompletar solicitud desde el historial reciente.** Si un paciente ya reportó síntomas similares en los últimos 30 días, ofrecer "¿Es una continuación de tu consulta anterior?" al abrir `/app/solicitudes/nueva` — reduce fricción de reingresar contexto ya conocido por el sistema.
2. **Modo "un solo dato a la vez" opcional para adultos mayores.** Un toggle de accesibilidad adicional (más allá de tamaño de texto/contraste) que muestre formularios largos como una secuencia de una pregunta por pantalla en vez de un formulario completo — reduce la carga cognitiva para la persona "Familiar del Paciente" (doc 01).
3. **Confirmación por voz en la guía de primeros auxilios.** Dado que `P-Emergencia-Activa` puede usarse con las manos ocupadas atendiendo a alguien, evaluar lectura en voz alta (Web Speech API) de cada paso, con avance por comando de voz ("siguiente") además del táctil.
4. **Deshacer en vez de confirmar, donde sea seguro.** Para acciones reversibles de bajo riesgo (ej. archivar un chip de filtro, descartar un borrador no crítico), reemplazar el modal de confirmación por un toast con "Deshacer" — reduce fricción sin sacrificar seguridad, reservando los modales de confirmación explícita para acciones genuinamente irreversibles (cierre de caso, eliminación).

## 14.2 Conversión (finalización de flujos)

5. **Reducir el punto de abandono en el registro.** Permitir "continuar como invitado" hasta el primer mensaje del chatbot de orientación (RF-02), pidiendo registro completo recién antes de enviar la solicitud formal (RF-03) — el valor (orientación) se entrega antes de pedir el costo (registro), aumentando la probabilidad de conversión en el momento de mayor motivación.
6. **Progreso visible y reversible en formularios largos de administración.** En `P-Admin-Centro-Form` (multi-sección), mostrar explícitamente cuántas secciones faltan y permitir guardar y volver — el abandono en formularios administrativos largos suele deberse a percepción de "esto no se acaba nunca", no a la dificultad real de cada campo.
7. **Recordatorio de teleconsulta con acción de un toque.** La notificación "Tu teleconsulta empieza en 5 minutos" (doc 10 §10.9) debe permitir unirse directamente desde la notificación push, sin pasar por el dashboard — cada paso intermedio es una oportunidad de abandono, especialmente relevante en población con baja alfabetización digital.

## 14.3 Claridad

8. **Traducir el nivel de confianza de la IA a lenguaje de riesgo, no de porcentaje, para el paciente.** El profesional ve "nivel de confianza: 87%" (dato técnico útil para su criterio clínico); el paciente nunca debería ver ese número crudo — para él, la traducción debe ser cualitativa ("Evaluamos tu caso con alta confianza según tus síntomas reportados"), evitando que un paciente ansioso sobre-interprete un número que no está calibrado para su lectura.
9. **Explicar el "por qué" del nivel de riesgo también al paciente, no solo al profesional.** Hoy la explicabilidad RAG (doc 04 §4.5) está diseñada para el profesional. Una versión simplificada y no clínica ("Tu evaluación se basó en la duración de tus síntomas y tu frecuencia cardíaca reportada") aumentaría la confianza del paciente en el sistema sin exponer el detalle técnico que no necesita.
10. **Glosario contextual inline para roles administrativos.** Términos como "validación M2M" o "consorcio" (visibles en `/app/admin/centros`) deberían tener un ícono "?" con definición en una sola línea — no todo administrador nuevo conoce la jerga interna del sistema desde el día uno.

## 14.4 Accesibilidad

11. **Modo de alto contraste real, no solo aumento de opacidad.** El switch de "Alto contraste" en `/app/configuracion/accesibilidad` (doc 04 §4.8) debería activar una paleta alternativa verdaderamente optimizada (contraste ≥7:1 en todo el sistema, no solo en alertas críticas), no simplemente oscurecer los tonos existentes — un ajuste cosmético insuficiente no resuelve el caso de uso real de baja visión.
12. **Subtítulos en tiempo real para teleconsulta.** Para pacientes con hipoacusia o en entornos ruidosos, transcripción en vivo (speech-to-text) del audio de la teleconsulta como panel opcional — impacto directo en el objetivo de accesibilidad WCAG que hoy cubre la interfaz pero no el contenido audiovisual en sí.
13. **Verificación de comprensión, no solo de entrega, en alertas críticas.** Para el familiar/paciente en `P-Emergencia-Activa`, considerar un patrón de confirmación mínima ("Toca aquí para confirmar que viste esta alerta") que garantice que la interfaz no solo mostró la alerta sino que hay evidencia de que fue percibida — relevante para el registro de auditoría de entrega de alertas (RNF-CONF-005).

## 14.5 Rendimiento percibido

14. **Precarga predictiva de la sala de teleconsulta.** ⚠️ Depende de que exista una "agenda" consultable (hoy no existe, ver doc 14.0/G3) — una vez resuelta esa brecha, precargar los permisos de cámara/micrófono y establecer la conexión WebRTC unos segundos antes de la hora programada (con consentimiento previo del usuario) elimina el tiempo de espera visible al momento de "Unirme a la consulta".
15. **Optimistic UI en confirmaciones de bajo riesgo.** Al marcar una notificación como leída o al aplicar un filtro, reflejar el cambio de inmediato en la interfaz sin esperar la respuesta del servidor (con reversión silenciosa si falla) — se siente instantáneo en vez de tener una latencia de red perceptible en acciones triviales.
16. **Streaming de la respuesta del LLM en el chat.** En vez de esperar la respuesta completa del bot de orientación (hasta 10s según RNF-PERF-001), mostrar el texto apareciendo progresivamente (igual que un chat de IA moderno) — reduce la percepción de espera aunque el tiempo total de generación sea el mismo.

## 14.6 Experiencia general

17. **Resumen post-atención descargable/compartible.** ⚠️ Depende primero de que exista el resumen en sí (bloqueado por G3, doc 14.0) — una vez que `teleconsult-service` guarde diagnóstico y lo cierre, ese resumen debería poder descargarse como PDF o compartirse directamente a otro profesional, reforzando la continuidad de cuidado (objetivo de producto, doc 01).
18. **Panel de "mi confianza en la IA" para profesionales, agregado en el tiempo.** Una vista opcional (no obligatoria para el MVP) donde el profesional vea cuántas veces ajustó manualmente el nivel de riesgo calculado por la IA en el último mes — información valiosa tanto para el profesional (calibrar su propia confianza en el sistema) como para el equipo de producto (detectar patrones sistemáticos de desacuerdo que ameriten revisar el modelo).
19. **Feedback ligero post-interacción con el bot de FAQ.** Un simple "¿Esto resolvió tu duda? Sí/No" tras cada respuesta del bot de orientación administrativa (RF-07) alimenta directamente la métrica de precisión de FAQ (NFR-FIAB-001) sin necesitar una encuesta separada.
20. **Considerar un modo "sala de espera compartida" para emergencias familiares.** Cuando varios familiares tienen acceso a la misma emergencia activa (doc 03 §3.8), mostrar de forma sutil quién más está viendo la pantalla en ese momento — reduce la ansiedad de sentir que se está solo con la decisión y evita duplicación de llamadas/acciones entre familiares.

---

## 14.7 Priorización sugerida (para discutir con producto)

| Prioridad | Recomendaciones | Justificación |
|---|---|---|
| **Bloqueante — antes que cualquier otra cosa** | Toda la tabla de **§14.0** (brechas de backend) | Sin esto, partes enteras del diseño en docs 02–04 no tienen nada que consumir — no es una mejora, es un prerrequisito |
| **Alta — antes del MVP** | #8/#9 (lenguaje de riesgo para paciente), #11 (alto contraste real) | Impacto directo en objetivos de producto ya declarados (doc 01) y en accesibilidad, que es requisito funcional, no opcional |
| **Media — primer incremento post-MVP** | #1, #6, #16 | Mejoras de conversión y claridad con costo de implementación moderado |
| **Baja — evaluar con datos de uso real** | #2, #3, #12, #13, #18, #19, #20 | Requieren validar necesidad real con usuarios antes de invertir — no asumir la solución sin evidencia de uso |
| **Depende de una brecha bloqueante resuelta primero** | #5 (registro diferido — depende de G2), #7 (recordatorio con acción directa — depende de G7), #14 (precarga teleconsulta — depende de G3), #17 (resumen descargable — depende de G3) | Son buenas ideas, pero no son implementables hasta que su brecha de backend correspondiente (§14.0) esté resuelta |
