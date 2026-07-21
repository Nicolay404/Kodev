# 01 — Estrategia UX
## SAMR — Sistema de Atención Médica Remota

---

## 1.1 Objetivos del producto

| Objetivo | Descripción | Métrica de éxito (fuente: NFR/RF) |
|---|---|---|
| **Reducir el tiempo entre síntoma y atención** | Comprimir la distancia entre que un paciente reporta un síntoma y recibe orientación, evaluación de riesgo o atención efectiva. | Orientación LLM ≤ 10s · Triage P95 ≤ 10s · Matching P95 ≤ 8s |
| **Garantizar continuidad clínica interinstitucional** | Un mismo expediente clínico consolidado, accesible por SAMR, MSP, IESS y los centros del consorcio, sin reingresar datos. | Intercambio exitoso con ≥ 2 sistemas externos vía HL7 FHIR |
| **Sostener confianza clínica y regulatoria en la IA** | Ninguna decisión de IA (triage, matching, recomendación) puede ser una caja negra: todo debe ser explicable, trazable y no editable retroactivamente. | 100% de decisiones de IA con registro append-only + fuente RAG |
| **No fallar en el peor momento** | El sistema debe sostener picos de demanda y nunca degradar silenciosamente ante una emergencia médica real. | Disponibilidad ≥ 99,9% en emergencias/historial · degradación ≤ 5% con 1.000 solicitudes simultáneas |
| **Ser usable por cualquiera, bajo estrés** | La interfaz no puede exigir alfabetización digital alta ni buena visión/motricidad para funcionar en el peor escenario (emergencia, adulto mayor, ansiedad). | WCAG 2.1 AA en todo flujo dirigido a paciente/familiar |

## 1.2 Objetivos del usuario (por rol)

| Rol | Lo que necesita lograr | Lo que teme / quiere evitar |
|---|---|---|
| Paciente / Familiar | Saber qué tan grave es lo que le pasa y qué hacer, rápido y sin tecnicismos | Sentir que "nadie lo está viendo", perder tiempo llenando formularios largos en una urgencia |
| Profesional de Salud | Decidir con información clínica confiable, priorizada y trazable | Que la IA le oculte el razonamiento, o que le haga perder tiempo confirmando lo obvio |
| Enfermero/Paramédico | Actuar en campo con instrucciones claras y accionables al instante | Quedarse sin conectividad en el peor momento, o recibir una alerta ambigua |
| Administrador de Centro Médico | Ver los casos de su centro y verificar su completitud | Comprometer un recurso que en realidad no está disponible — objetivo aspiracional: hoy no existe ninguna acción de "confirmar disponibilidad" en el backend (ver [00](00-alineacion-backend.md) §G13), es el rol con menor superficie funcional real del sistema |
| Administrador de SAMR | Mantener el catálogo de centros y dispositivos íntegro y auditable | Registrar datos corruptos o incompletos que rompan flujos aguas abajo |
| Delegado de Protección de Datos (DPD) | Auditar decisiones de IA con evidencia completa, sin fricción de acceso | No poder explicar una decisión ante un ente regulador |

## 1.3 Problemas que resuelve la plataforma

1. **Fragmentación del primer contacto médico**: hoy el paciente no sabe si su síntoma amerita ir a urgencias, esperar, o es manejable en casa — SAMR da una primera orientación inmediata (chatbot + LLM) antes de cualquier trámite.
2. **Priorización clínica manual y lenta**: sin triage automatizado, todos los casos compiten por el mismo tiempo de un profesional — SAMR calcula el nivel de riesgo y escala automáticamente los casos críticos.
3. **Desconexión entre monitoreo en casa y atención médica**: los datos de dispositivos IoT (glucómetros, oxímetros, ECG) no suelen llegar a nadie que pueda actuar sobre ellos en tiempo real — SAMR los ingiere, analiza anomalías y puede generar una solicitud automática.
4. **Expedientes fragmentados entre instituciones**: el historial de un paciente vive disperso entre el centro que lo atendió, el MSP y el IESS — SAMR consolida un expediente único e interoperable (FHIR).
5. **Decisiones de IA no auditables en salud**: usar IA en un contexto clínico sin trazabilidad es un riesgo regulatorio y ético — SAMR registra cada decisión de forma inalterable, con evidencia RAG y revisión DPD.
6. **Emergencias sin apoyo mientras llega ayuda**: el tiempo entre "algo grave está pasando" y que llegue un profesional es el más peligroso — SAMR entrega una guía de primeros auxilios generada al instante mientras se despacha ayuda.

## 1.4 Propuesta de valor

> **Para** pacientes y familiares que enfrentan un problema de salud sin saber qué tan urgente es,
> **SAMR es** una plataforma de atención médica remota asistida por IA
> **que** orienta, evalúa el riesgo, conecta con el profesional adecuado y mantiene un expediente clínico único e interoperable,
> **a diferencia de** una línea de atención telefónica o un portal de citas tradicional,
> **SAMR** prioriza automáticamente según gravedad clínica real, es explicable y auditable en cada decisión de IA, y no interrumpe la continuidad del cuidado entre instituciones.

## 1.5 Público objetivo

| Segmento | Descripción | Contexto de uso dominante |
|---|---|---|
| Pacientes y familiares — población general | Todas las edades, todos los niveles de alfabetización digital, incluida población adulta mayor | Móvil, a menudo bajo estrés o urgencia |
| Profesionales de la salud afiliados al consorcio | Médicos generales y especialistas que atienden por teleconsulta | Desktop/tablet, en jornada laboral o guardia |
| Personal de campo (enfermería/paramédicos) | Responde emergencias y actualiza historiales en sitio | Móvil, conectividad variable |
| Personal administrativo de centros médicos del consorcio | Gestiona disponibilidad de recursos y cierre de casos | Desktop, en horario administrativo |
| Administración SAMR | Equipo interno que mantiene catálogo de centros/dispositivos | Desktop, tareas de backoffice |
| Delegado de Protección de Datos | Rol de cumplimiento normativo (LOPDP Ecuador) | Desktop, sesiones de auditoría periódicas |

**Confirmado contra el backend real (`auth-service/apps/auth/models.py`, ver [00](00-alineacion-backend.md) §0.1)**: los 6 roles de esta lista existen exactamente así en el enum `ROLE_CHOICES` del modelo `User` — ya no es un supuesto. Lo que sigue siendo **[SUPUESTO]** es "Familiar del Paciente": no existe un rol `familiar` en el backend; el registro público (`POST /api/auth/register/`) siempre crea rol `patient` sin excepción. Se asume que el familiar opera con una cuenta de tipo `patient` vinculada o delegada al paciente real, sin excluir que en una fase posterior se modele como relación (`cuidador_de`) sobre el mismo perfil — esa relación no existe hoy en ningún modelo del backend.

---

## 1.6 User Personas

### Persona 1 — Paciente

| Campo | Detalle |
|---|---|
| **Nombre** | María Fernanda Solano |
| **Edad / rol** | 34 años, madre, trabaja medio tiempo |
| **Contexto** | Vive en zona periurbana de Quito, cobertura de datos móviles intermitente |
| **Dispositivo principal** | Smartphone gama media, conexión 4G |
| **Alfabetización digital** | Media — usa WhatsApp, apps bancarias, pero se frustra con formularios largos |
| **Objetivo** | Entender rápido si el dolor abdominal de su hijo requiere ir a emergencias o puede esperar |
| **Frustraciones** | Líneas de atención telefónica con espera larga; portales de salud que piden repetir toda su historia clínica cada vez |
| **Necesidades UX** | Lenguaje simple, sin jerga médica; poder corregir un dato sin reiniciar todo el flujo; ver progreso real, no un spinner vacío |
| **Cita** | *"No quiero saber el nombre del protocolo, quiero saber si tengo que salir corriendo al hospital."* |

### Persona 2 — Familiar del Paciente (cuidador)

| Campo | Detalle |
|---|---|
| **Nombre** | Jorge Andrade |
| **Edad / rol** | 58 años, cuida a su madre de 82 años con hipertensión |
| **Contexto** | Reporta síntomas y monitorea datos biomédicos en nombre de su madre, que no usa smartphone |
| **Dispositivo principal** | Tablet en casa, smartphone fuera |
| **Alfabetización digital** | Media-baja, requiere texto grande y navegación sin ambigüedad |
| **Objetivo** | Recibir alertas claras cuando el dispositivo de monitoreo de su madre detecta algo anómalo, y saber exactamente qué hacer |
| **Frustraciones** | No saber si una alerta es "urgente de verdad" o solo informativa; miedo a tomar la decisión equivocada |
| **Necesidades UX** | Jerarquía de urgencia inequívoca (color + ícono + texto); notificaciones que no dejen lugar a interpretación |
| **Cita** | *"Cuando el reloj de mi mamá me manda una alerta, necesito saber en tres segundos si es grave."* |

### Persona 3 — Profesional de la Salud / Evaluador Clínico

| Campo | Detalle |
|---|---|
| **Nombre** | Dra. Priscila Nájera |
| **Edad / rol** | 41 años, medicina interna, atiende teleconsultas del consorcio |
| **Contexto** | Revisa entre 15 y 20 casos por turno, alterna teleconsulta con revisión de casos escalados |
| **Dispositivo principal** | Laptop, doble monitor en el centro médico |
| **Alfabetización digital** | Alta, pero con poca paciencia para UI ineficiente |
| **Objetivo** | Confiar en el nivel de riesgo calculado por la IA sin tener que re-verificar todo manualmente |
| **Frustraciones** | Herramientas clínicas que ocultan el "por qué" de una recomendación; UI que le hace clickear de más en momentos críticos |
| **Necesidades UX** | Explicabilidad de IA visible sin fricción (un clic, no una página aparte); atajos de teclado; información densa pero escaneable |
| **Cita** | *"Puedo confiar en la IA si me muestra en qué se basó. Si no, la ignoro — y eso también es un riesgo."* |

### Persona 4 — Enfermero/Paramédico

| Campo | Detalle |
|---|---|
| **Nombre** | Kevin Morales |
| **Edad / rol** | 27 años, paramédico de ambulancia afiliada al consorcio |
| **Contexto** | Recibe alertas de emergencia en movimiento, actualiza historial desde el lugar del incidente |
| **Dispositivo principal** | Smartphone robusto, a veces sin señal estable |
| **Alfabetización digital** | Media-alta, pero sin tiempo para leer interfaces complejas en campo |
| **Objetivo** | Recibir la guía de primeros auxilios y los datos del paciente al instante, y no perder el registro si se corta la conexión |
| **Frustraciones** | Apps que exigen conexión constante; información crítica enterrada en menús |
| **Necesidades UX** | Diseño mobile-first, texto legible al sol, reconexión automática con aviso claro de estado offline |
| **Cita** | *"Cuando llego a una emergencia tengo segundos, no minutos, para entender qué está pasando."* |

### Persona 5 — Administrador de Centro Médico

| Campo | Detalle |
|---|---|
| **Nombre** | Lucía Peñaherrera |
| **Edad / rol** | 45 años, coordinadora administrativa de un centro del consorcio |
| **Contexto** | Revisa casos del centro y verifica su completitud varias veces al día |
| **Dispositivo principal** | Desktop de oficina |
| **Alfabetización digital** | Media-alta, orientada a tareas repetitivas eficientes |
| **Objetivo** | Verificar que un caso esté completo — el cierre en sí lo ejecuta el profesional tratante, no ella *(ver [00](00-alineacion-backend.md) §G9: el cierre es exclusivo del rol Profesional)* |
| **Frustraciones** | Tener que buscar información dispersa antes de poder verificar algo; no tener visibilidad de recursos del centro para confirmarlos (§G13 — sin API de disponibilidad hoy) |
| **Necesidades UX** | Tablas accionables, checklist de completitud visible |
| **Cita** | *"Necesito ver de un vistazo si un caso está listo para cerrarse — aunque el botón de cerrar ya no sea mío."* |

### Persona 6 — Administrador de SAMR

| Campo | Detalle |
|---|---|
| **Nombre** | Diego Salazar |
| **Edad / rol** | 38 años, administrador de plataforma del equipo SAMR |
| **Contexto** | Registra y valida centros médicos nuevos y dispositivos IoT |
| **Dispositivo principal** | Desktop |
| **Alfabetización digital** | Alta |
| **Objetivo** | Que ningún registro incompleto o mal formado llegue a corromper el catálogo | 
| **Frustraciones** | Formularios sin validación clara que permiten guardar datos basura |
| **Necesidades UX** | Validación en tiempo real por campo, feedback inmediato de por qué algo fue rechazado |
| **Cita** | *"Prefiero que el formulario me detenga ahora a que el error aparezca en producción con un paciente real detrás."* |

### Persona 7 — Delegado de Protección de Datos (DPD)

| Campo | Detalle |
|---|---|
| **Nombre** | Abg. Carla Ibarra |
| **Edad / rol** | 50 años, oficial de cumplimiento LOPDP |
| **Contexto** | Revisa periódicamente la trazabilidad de decisiones de IA |
| **Dispositivo principal** | Desktop |
| **Alfabetización digital** | Media, orientada a lectura y revisión, no a operación |
| **Objetivo** | Poder sustentar ante un ente regulador que cada decisión automatizada es explicable | 
| **Frustraciones** | Registros incompletos, o tener que pedir información adicional a otro equipo para auditar |
| **Necesidades UX** | Vista de auditoría completa en un solo lugar, exportable, con estado de revisión claro |
| **Cita** | *"Mi trabajo es poder responder '¿por qué la IA decidió esto?' sin depender de que alguien más me lo explique."* |

---

## 1.7 Escenarios de uso

**Escenario A — Consulta no urgente (Paciente, M1→M2→M3).**
María nota que su hijo tiene fiebre baja hace dos días. Abre SAMR, conversa con el bot, reporta síntomas, el sistema calcula riesgo "moderado", y le asigna una teleconsulta con un pediatra en menos de una hora, sin necesidad de salir de casa.

**Escenario B — Emergencia con dispositivo IoT (Familiar, M1 flujo alterno→M3 emergencia).**
El reloj de monitoreo de la madre de Jorge detecta una arritmia. El sistema genera una solicitud automática, la escala directamente (riesgo crítico), emite una alerta a Jorge con una guía de primeros auxilios mientras despacha una ambulancia con un paramédico.

**Escenario C — Triage y decisión clínica (Profesional de Salud, M2).**
La Dra. Nájera revisa un caso escalado por IA a "riesgo alto". Ve el nivel de riesgo y las fuentes RAG que lo sustentan, y ejecuta el matching — el sistema asigna automáticamente el centro disponible *(ver [00](00-alineacion-backend.md) §G5: hoy no hay lista de centros entre los que elegir)*.

**Escenario D — Atención en campo (Paramédico, M3 emergencia).**
Kevin recibe la alerta de emergencia en su teléfono mientras conduce la ambulancia. Ve la guía de primeros auxilios y los datos relevantes del paciente antes de llegar, y **consulta** (lectura, no puede editar — ver [00](00-alineacion-backend.md) §G12) el historial existente del paciente para saber alergias y condiciones crónicas antes de intervenir.

**Escenario E — Cierre y continuidad (Profesional de Salud, M3→M4).**
Un profesional revisa que el caso, originado por una emergencia despachada, tenga notas clínicas completas antes de confirmar el cierre *(exclusivo del rol Profesional — ver [00](00-alineacion-backend.md) §G9; el Administrador de Centro Médico ya no participa en esta acción, solo puede verificar completitud sin cerrar)*, lo que dispara la consolidación del expediente hacia el historial único.

**Escenario F — Administración de catálogo (Administrador SAMR, M4).**
Diego registra un nuevo centro médico del consorcio; el sistema valida el formulario en tiempo real y envía la solicitud a validación M2M con el Consorcio, notificándole el resultado.

**Escenario G — Auditoría regulatoria (DPD, M4).**
Carla necesita revisar todas las decisiones de IA de nivel "crítico" del último mes para un reporte de cumplimiento. Filtra por fecha y nivel, revisa la explicabilidad de cada una, y marca su estado de revisión.

---

## 1.8 User Journey Maps

### Journey 1 — Paciente: de síntoma a teleconsulta (Escenario A)

| Etapa | Acción | Pensamiento | Emoción | Touchpoint | Fricción / Oportunidad |
|---|---|---|---|---|---|
| Detección | Nota el síntoma de su hijo | "¿Esto es grave?" | Incertidumbre | — | Oportunidad: orientación inmediata sin registro previo |
| Orientación | Conversa con el bot | "Ojalá me entienda sin que tenga que explicar tres veces" | Cautela | Chat / voicebot | Riesgo: si el bot no reconoce la intención, frustra de inmediato |
| Registro | Completa datos de síntomas | "Espero que esto no tarde" | Ligera ansiedad | Formulario de solicitud | Oportunidad: autocompletar con datos del dispositivo IoT si existe |
| Espera de validación | El Consorcio valida la solicitud | "¿Ya la vieron?" | Expectante | Estado de solicitud | ⚠️ **Brecha de backend (ver [00](00-alineacion-backend.md) §G2)**: no hay ningún endpoint para consultar este estado — el paso se diseña como aspiracional hasta que exista |
| Evaluación | Sistema calcula riesgo | (no visible directamente) | — | — | Única señal real disponible: `GET /api/evaluacion/riesgo/{id}/` (200 si ya evaluada, 404 si no) — mensaje contextual mientras se hace polling |
| Asignación | Recibe notificación de teleconsulta asignada | "Qué alivio, ya tengo hora" | Alivio | Push / in-app | ⚠️ Notificaciones sin backend hoy (§G7); el `room_token` de la sala tampoco es consultable por el paciente (§G4) |
| Atención | Entra a la teleconsulta | "Espero que el video funcione bien" | Expectación | Sala de teleconsulta | Riesgo: fallo de conexión sin reintento visible |
| Cierre | Recibe diagnóstico y recomendaciones | "Ya sé qué hacer" | Tranquilidad | Resumen post-consulta | ⚠️ **Brecha de backend (§G3)**: no existe endpoint de cierre ni de guardado de diagnóstico — este paso no es realizable con el backend actual |

### Journey 2 — Familiar: emergencia crítica (Escenario B)

| Etapa | Acción | Pensamiento | Emoción | Touchpoint | Fricción / Oportunidad |
|---|---|---|---|---|---|
| Alerta | Recibe notificación de anomalía | "¿Qué pasó?" | Alarma | Push crítico | Debe ser inconfundible: color+ícono+sonido |
| Comprensión | Ve el nivel "crítico" | "Tengo que actuar YA" | Pánico | Pantalla de alerta | Cero fricción — un solo vistazo debe bastar |
| Acción guiada | Recibe guía de primeros auxilios | "¿Qué hago mientras llega ayuda?" | Urgencia con foco | Guía de primeros auxilios | Debe ser accionable paso a paso, sin scroll largo |
| Espera de ayuda | Ve el estado del despacho de ambulancia | "¿Cuánto falta?" | Ansiedad | Estado de emergencia | Oportunidad: estimado de tiempo, aunque sea aproximado |
| Llegada de ayuda | El paramédico llega y toma el caso | "Ya no estoy solo con esto" | Alivio | — | — |

### Journey 3 — Profesional de Salud: evaluación y decisión (Escenario C)

| Etapa | Acción | Pensamiento | Emoción | Touchpoint | Fricción / Oportunidad |
|---|---|---|---|---|---|
| Notificación | Ve el caso escalado en su cola | "¿Qué tan urgente es realmente?" | Neutral-atenta | Dashboard clínico | Priorización visual clara por nivel de riesgo — ordenamiento se hace en cliente, la API devuelve los 50 casos más recientes de todo el sistema sin filtrar por profesional (ver 00 §0.3, M2) |
| Revisión | Abre el detalle del caso | "¿En qué se basó la IA?" | Analítica | Vista de evaluación de riesgo | Explicabilidad a un clic, no oculta; el nivel de riesgo es de solo lectura — no hay forma de corregirlo desde la API (00 §0.3, M3) |
| Decisión | Ejecuta el matching (un solo paso, sin elegir centro) | "Espero que asigne bien" | Decisiva | Acción de matching | El backend auto-asigna el centro; no hay lista de candidatos que confirmar (ver [00](00-alineacion-backend.md) §G5) |
| Atención | Inicia teleconsulta | "A trabajar" | Enfocada | Sala de teleconsulta | Asistencia IA disponible sin interrumpir el flujo clínico |
| Registro | Documenta diagnóstico | "Que quede bien registrado" | Metódica | Formulario de cierre | ⚠️ **Brecha de backend (§G3)**: no hay endpoint para guardar diagnóstico de una teleconsulta; el cierre formal de caso solo es alcanzable hoy por la vía de emergencia |

### Journey 4 — Administrador SAMR: registro de centro médico (Escenario F)

| Etapa | Acción | Pensamiento | Emoción | Touchpoint | Fricción / Oportunidad |
|---|---|---|---|---|---|
| Inicio | Abre el formulario de registro | "Espero que sea directo" | Neutral | Panel admin | — |
| Carga de datos | Llena datos del centro | "¿Falta algo?" | Concentrada | Formulario multi-sección | Validación en tiempo real por campo |
| Envío | Envía a validación M2M | "¿Cuánto tarda esto?" | Expectante | Estado "pendiente de validación" | La validación real es automática y casi instantánea (no hay revisión humana detrás) |
| Resultado | Recibe validación o rechazo | "¿Por qué lo rechazaron?" (si aplica) | Alivio / frustración | Notificación | ⚠️ **Brecha de backend (ver [00](00-alineacion-backend.md) §G6)**: no existe ningún endpoint para consultar el resultado — un rechazo es hoy completamente invisible para el admin; solo un centro validado aparece más tarde en el catálogo de disponibles |

---

## 1.9 Customer Journey (nivel institucional)

A diferencia de los User Journeys (nivel tarea), el Customer Journey describe el ciclo de vida de adopción de SAMR por parte de un **centro médico del consorcio**, que es quien decide integrarse a la plataforma:

| Fase | Descripción | Rol dominante | Objetivo de UX |
|---|---|---|---|
| **Conocimiento** | El centro médico conoce SAMR a través del consorcio/MSP/IESS | — (fuera del producto) | Material de onboarding claro fuera de la app |
| **Incorporación** | Administrador SAMR registra el centro; pasa por validación M2M | Administrador SAMR | Proceso de alta sin fricción, feedback de estado constante |
| **Activación** | El centro empieza a recibir casos asignados por matching | Administrador de Centro Médico, Profesionales | Primeros casos deben sentirse simples de gestionar |
| **Uso recurrente** | Profesionales atienden teleconsultas y emergencias regularmente | Profesional, Paramédico | Eficiencia y confianza en la IA sostenidas en el tiempo |
| **Interoperabilidad plena** | El centro sincroniza expedientes con MSP/IESS de forma rutinaria | Administrador de Centro Médico | Sincronización invisible, sin trabajo manual repetido |
| **Auditoría / renovación de confianza** | DPD y administración revisan cumplimiento periódicamente | DPD | Evidencia de cumplimiento disponible sin fricción |

---

## 1.10 Jobs To Be Done (JTBD)

Formato: *Cuando [situación], quiero [motivación], para poder [resultado esperado].*

**Paciente / Familiar**
- Cuando no sé si un síntoma es grave, quiero una primera orientación confiable e inmediata, para decidir si debo actuar ahora o puedo esperar.
- Cuando mi solicitud ya fue registrada, quiero saber en qué estado está sin tener que preguntar, para no sentir que quedó en el vacío.
- Cuando hay una emergencia real, quiero instrucciones claras de qué hacer mientras llega ayuda, para no sentirme paralizado.

**Profesional de Salud**
- Cuando reviso un caso escalado por IA, quiero ver en qué se basó la evaluación, para poder confiar en la recomendación (el nivel de riesgo es de solo lectura hoy — ver [00](00-alineacion-backend.md) §0.3 M3 — así que documentar el desacuerdo clínico en las notas del cierre es, por ahora, la única vía).
- Cuando ejecuto el matching de un caso, quiero saber de inmediato si el sistema encontró un centro disponible, para no dejar al paciente sin recurso asignado sin darme cuenta.

**Enfermero/Paramédico**
- Cuando recibo una alerta de emergencia, quiero la información esencial del paciente de inmediato, para actuar sin perder tiempo revisando historiales largos.
- Cuando despacho una emergencia, quiero que quede confirmado de inmediato, para que el paciente y su familia sepan que la ayuda ya viene en camino.

**Administrador de Centro Médico**
- Cuando reviso un caso de mi centro, quiero verificar que esté completo, para poder señalarle al profesional tratante qué falta antes de que lo cierre *(la acción de cerrar ya no es suya — ver [00](00-alineacion-backend.md) §G9)*.

**Administrador de SAMR**
- Cuando registro un centro o dispositivo nuevo, quiero saber de inmediato si algo está mal formado, para no propagar datos corruptos al resto del sistema.

**Delegado de Protección de Datos**
- Cuando debo sustentar una decisión de IA ante un regulador, quiero acceder a su trazabilidad completa en un solo lugar, para no depender de otros equipos para responder.
