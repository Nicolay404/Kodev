# 06 - Design System
## SAMR - Sistema de Atención Médica Remota

> Todo componente interactivo se construye sobre su primitiva **Radix UI** equivalente (headless - ya trae focus trap, roles ARIA y manejo de teclado resueltos) y se estiliza con **Tailwind CSS** usando los tokens del doc 05. No se reconstruyen desde cero comportamientos que Radix ya resuelve (ver `ARQUITECTURA_MAESTRA_SAMR_v4.md` §5.6). Estados obligatorios para todo componente interactivo: **default, hover, focus, active, disabled**, más **error/success** donde aplique.

---

## 6.1 Botón

**Primitiva**: elemento nativo `<button>` estilizado (no requiere Radix).

| Variante | Uso | Fondo | Texto |
|---|---|---|---|
| `primary` | Acción principal de la pantalla (1 por vista) | `teal-600` | Blanco |
| `secondary` | Acción alternativa | Transparente, borde `gray-300` | `gray-800` |
| `destructive` | Acciones irreversibles (cerrar caso, eliminar) | `error-600` | Blanco |
| `ghost` | Acciones terciarias, dentro de tablas/toolbars | Transparente | `gray-700` |
| `link` | Navegación inline | Transparente | `teal-600` subrayado en hover |

| Estado | Tratamiento |
|---|---|
| Hover | `primary`→`teal-700`; `secondary`→ fondo `gray-50` |
| Focus | Anillo `2px teal-600` offset 2px, visible siempre por teclado |
| Active | Escala 0.98 (feedback táctil, ver doc 08) |
| Disabled | Opacidad 40%, cursor `not-allowed`, sin hover |
| Loading | Reemplaza el label por spinner de 16px + texto "Procesando…", mantiene el ancho del botón (evita salto de layout) |

**Tamaños**: `sm` (32px alto, texto sm), `md` (40px, texto base - por defecto), `lg` (48px, texto lg - usado en flujos de paciente/emergencia).
**Área táctil mínima**: 44×44px en `md` y `lg` incluyendo padding, incluso si el contenido visual es menor.

---

## 6.2 Input de texto

**Primitiva**: `<input>` nativo + `Label` asociado por `htmlFor`.

| Estado | Borde | Fondo | Extra |
|---|---|---|---|
| Default | `gray-300` | Blanco | - |
| Focus | `teal-600` 2px | Blanco | Anillo de foco visible |
| Error | `error-600` 2px | `error-50` sutil | Mensaje inline debajo, ícono de error a la derecha |
| Success (validación en tiempo real) | `success-600` 1px | Blanco | Ícono de check a la derecha |
| Disabled | `gray-200` | `gray-100` | Texto `gray-400` |

Tamaño único: 40px alto (`md`), 48px en formularios dirigidos a paciente (`lg`). Padding horizontal `space-3` (12px). Placeholder siempre en `gray-400`, nunca como único método de instrucción (ver doc 09).

---

## 6.3 Select

**Primitiva**: Radix `Select`.

Mismo tratamiento visual que Input. El trigger muestra chevron a la derecha (Lucide `chevron-down`, 16px). El contenido desplegable (`Select.Content`) usa `shadow-lg`, `radius-md`, máximo 7 ítems visibles antes de hacer scroll interno. Ítem activo con fondo `teal-50` y check a la izquierda (Radix `Select.ItemIndicator`).

---

## 6.4 Checkbox

**Primitiva**: Radix `Checkbox`.

| Estado | Tratamiento |
|---|---|
| Unchecked | Borde `gray-300` 2px, fondo blanco, `radius-sm` |
| Checked | Fondo `teal-600`, ícono check blanco |
| Indeterminate | Fondo `teal-600`, ícono guion |
| Focus | Anillo `2px teal-600` |
| Disabled | Opacidad 40% |
| Error | Borde `error-600` (usado en checkboxes de consentimiento LOPDP obligatorios) |

Tamaño: 20×20px caja, área táctil mínima 44×44px (padding invisible alrededor). Label siempre clickeable (asociado, no solo decorativo).

---

## 6.5 Radio Button

**Primitiva**: Radix `RadioGroup`.

Igual sistema de estados que Checkbox, forma circular. Usado en selección única (ej. nivel de disponibilidad, tipo de dispositivo). Nunca más de 6 opciones visibles sin agrupar - más de eso, usar `Select`.

---

## 6.6 Switch

**Primitiva**: Radix `Switch`.

| Estado | Fondo del track | Posición del thumb |
|---|---|---|
| Off | `gray-300` | Izquierda |
| On | `teal-600` | Derecha |
| Focus | Anillo `2px teal-600` alrededor del track | - |
| Disabled | Opacidad 40% | - |

Usado en `/app/configuracion/notificaciones` y `/app/configuracion/accesibilidad`. Todo switch va acompañado de label textual visible a su izquierda - nunca un switch huérfano sin descripción.

---

## 6.7 Card

Contenedor base: `bg-surface`, `radius-lg`, `shadow-sm` en reposo, `shadow-md` en hover si es clickeable (cursor `pointer`). Padding interno `space-4` a `space-6` según densidad.

| Variante | Uso |
|---|---|
| `card-default` | Contenido general (resumen de dashboard) |
| `card-interactive` | Clickeable, navega a detalle (ej. tarjeta de caso) |
| `card-urgencia` | Borde izquierdo de 4px con el color de urgencia correspondiente + badge (ver doc 06.15) |
| `card-stat` | KPI/métrica: número grande (`text-3xl`) + label (`text-sm` `gray-500`) |

---

## 6.8 Tabs

**Primitiva**: Radix `Tabs`.

Fila horizontal, subrayado de 2px `teal-600` bajo el tab activo (transición 150ms, ver doc 08). Tab inactivo: `gray-600`; hover: `gray-900`. En mobile, tabs con overflow horizontal scrolleable (nunca se comprimen ilegibles).

---

## 6.9 Sidebar

Ancho fijo 260px en desktop, colapsable a 72px (solo íconos, con tooltip al hover). En mobile se convierte en drawer (overlay) accionado desde el navbar (ver doc 07). Ítem activo: fondo `teal-50`, texto `teal-700`, borde izquierdo 3px `teal-600`. Ítems agrupados por sección con label `text-xs` `gray-400` uppercase como separador (sin línea divisoria visible, solo espaciado `space-6`).

---

## 6.10 Navbar

Altura fija 64px, `bg-surface`, `shadow-sm`, siempre fijo (`sticky top-0`). Contenido según doc 02 §2.6. Z-index superior a sidebar pero inferior a modales/toasts.

---

## 6.11 Footer

Minimalista, presente solo en páginas públicas (`/login`, `/registro`) - no dentro del shell autenticado (`/app/*`), donde el espacio vertical se prioriza para contenido clínico. Contiene: enlaces a política de privacidad (LOPDP), términos, contacto de soporte.

---

## 6.12 Breadcrumb

Ver reglas completas en doc 02 §2.7. Estilo: texto `text-sm` `gray-500`, separador `/` en `gray-300`, último segmento (actual) en `gray-900` sin link.

---

## 6.13 Tooltip

**Primitiva**: Radix `Tooltip`.

Fondo `gray-900` (ambos modos), texto blanco `text-xs`, `radius-sm`, `shadow-md`, aparece tras 400ms de hover/focus (evita parpadeo en paso rápido del mouse), max-width 240px. **Nunca** contiene la única explicación de un ícono crítico - siempre complementa un label visible o un `aria-label`, nunca lo reemplaza (doc 09).

---

## 6.14 Toast

**Primitiva**: `react-hot-toast` (definido en arquitectura v4) estilizado a tokens SAMR.

| Variante | Ícono | Borde izquierdo |
|---|---|---|
| Success | Check | `success-600` |
| Error | X circular | `error-600` |
| Warning | Triángulo | `warning-500` |
| Info | Info circular | `info-600` |

Posición: esquina superior derecha en desktop, ancho completo con margen en mobile. Duración: 5s por defecto, **infinito con botón de cerrar manual para errores críticos** (nunca un error de sistema desaparece solo). Máximo 3 toasts simultáneos visibles (apilados), el resto en cola.

---

## 6.15 Alerta (banner inline, distinta del Toast - persiste en el layout, no flota)

| Variante | Uso |
|---|---|
| `alerta-critico` | Banner de emergencia activa (fijo bajo navbar, ver doc 02 §2.6) |
| `alerta-info` | Avisos contextuales dentro de una página (ej. "Evidencia RAG no disponible temporalmente") |
| `alerta-warning` | Datos pendientes de completar |

Estructura: ícono + texto + acción opcional (botón/link) a la derecha. `radius-md`, padding `space-4`, fondo del color semántico al 10% de opacidad + borde izquierdo 4px sólido del mismo color + texto en el tono `-700` correspondiente (garantiza contraste).

---

## 6.16 Chip

Pill pequeño, `radius-full`, `text-xs`, padding `space-1` `space-3`. Usado para filtros activos (ej. `/app/casos` filtrado por especialidad) - incluye botón "x" para remover.

---

## 6.17 Badge

Igual forma que Chip pero no removible - comunica estado (ej. "Validado", "Pendiente"). Variantes de color = variantes semánticas (doc 05 §5.1). Los badges de **nivel de riesgo/urgencia son el único badge que además lleva ícono**, por la regla de semiótica redundante.

---

## 6.18 Etiqueta (Label / Tag de metadatos)

Texto `text-xs` `gray-500` uppercase, `letter-spacing: 0.05em`, usado como microcopy identificador sobre un valor (ej. "NIVEL DE RIESGO" sobre el badge correspondiente). No confundir con `<label>` de formulario (que usa `text-sm` `gray-700` sin uppercase, por legibilidad - el uppercase reduce legibilidad en texto largo).

---

## 6.19 Calendario / Selector de fecha

**Primitiva**: Radix `Popover` + lógica de calendario custom (react-day-picker o equivalente compatible con Radix).

Usado en `/app/auditoria` (filtro de fecha, client-side sobre los 100 registros ya cargados - ver [00](00-alineacion-backend.md) §0.3 M6). Día actual con borde `teal-600`; día seleccionado con fondo `teal-600` sólido y texto blanco; rango seleccionado con fondo `teal-50`. *(No se usa en teleconsultas - no existe una "agenda" consultable, ver §G3.)*

---

## 6.20 Tabla

Fila alterna sin zebra-stripe agresivo (solo `gray-50` en hover de fila, no por defecto - reduce ruido visual). Header `text-xs` uppercase `gray-500`, sticky al hacer scroll vertical en tablas largas. Columna de acciones siempre a la derecha, con menú `⋮` (Dropdown, ver 6.24) si hay más de 2 acciones.

**Regla de densidad**: tablas de uso profesional (`/app/casos`, `/app/auditoria`) usan densidad compacta (`space-2` vertical por celda); tablas dirigidas a paciente (`/app/solicitudes` en vista lista) usan densidad cómoda (`space-4`).

**Responsive**: por debajo de `md` breakpoint, la tabla se transforma en lista de Cards apiladas (ver doc 07) - nunca scroll horizontal forzado como única solución.

---

## 6.21 Paginación

Controles: anterior/siguiente + números de página (máximo 5 visibles + elipsis). En listados largos de uso profesional se prioriza **scroll infinito con carga progresiva** sobre paginación clásica (menos fricción para revisar muchos casos seguidos); paginación clásica se reserva para `/app/admin/*` y `/app/auditoria` donde la navegación a una página específica es más relevante que el scroll continuo.

---

## 6.22 Avatar

Circular (`radius-full`), tamaños 24/32/40/48px. Fallback: iniciales sobre fondo de color determinístico (hash del nombre → una de las variantes semánticas en tono `-100` con texto `-700`), nunca un ícono de silueta genérica - más humano y reconocible en listas.

---

## 6.23 Menú (contextual)

**Primitiva**: Radix `Menu` / `ContextMenu`.

Igual tratamiento visual que Dropdown (6.24). Activado por clic derecho o botón `⋮` explícito - nunca como único medio de acceso a una acción (debe existir alternativa accesible por teclado/tab).

---

## 6.24 Dropdown Menu

**Primitiva**: Radix `DropdownMenu`.

`shadow-lg`, `radius-md`, `bg-surface`, ítems con padding `space-2` `space-3`, hover `gray-50` (`gray-700` en modo oscuro). Separadores (`DropdownMenu.Separator`) entre grupos de acciones destructivas y no destructivas - la acción destructiva siempre va al final, en `error-600`.

---

## 6.25 Modal

**Primitiva**: Radix `Dialog`.

Overlay `rgba(15,23,42,0.5)`, contenido centrado `radius-lg`, `shadow-xl`, max-width 480px (formularios simples) o 640px (formularios multi-sección). Focus trap automático (provisto por Radix), cierre con `Escape` y clic en overlay **excepto** en modales de confirmación de acción irreversible (cierre de caso, eliminación), donde solo se cierra con acción explícita del usuario (evita cierres accidentales que interrumpan un flujo crítico).

Estructura: título (`text-xl` `font-semibold`) + descripción opcional + contenido + footer con acciones (`secondary` a la izquierda / `primary` o `destructive` a la derecha).

---

## 6.26 Accordion

**Primitiva**: Radix `Accordion`.

Usado en `/app/ayuda` (FAQ) y en secciones opcionales de formularios largos. Ícono chevron rota 180° en transición 150ms al expandir (ver doc 08). *(El formulario de registro de centro médico ya no usa este patrón - es una sola sección, ver doc 04 y [00](00-alineacion-backend.md) §G6.)*

---

## 6.27 Timeline

Usado en `/app/historial` - línea vertical `gray-200` con nodos circulares por evento, coloreados según tipo (solicitud=`teal`, teleconsulta=`indigo`, emergencia=`error`, decisión IA=`gray-800` con ícono de IA). Cada nodo expande su detalle inline (no navega a otra pantalla) para mantener el contexto temporal visible.

---

## 6.28 Progress Bar

Usado **solo** para procesos con progreso real medible (ej. subida de un archivo adjunto). **Explícitamente prohibido** como indicador de procesos de IA (evaluación de riesgo, matching) - ver doc 03/08, ahí se usan mensajes contextuales + Skeleton, nunca una barra con porcentaje inventado.

Altura 6px, `radius-full`, fondo `gray-200`, relleno `teal-600` con transición de ancho `width 300ms ease-out`.

---

## 6.29 Skeleton Loader

Bloques `gray-200` (modo claro) / `gray-700` (modo oscuro), `radius-md`, con animación shimmer (ver doc 08). La forma del skeleton **debe replicar la forma real del contenido que va a cargar** (card de caso → skeleton con la misma disposición de badge+título+meta), nunca un rectángulo genérico - reduce el "salto" de layout percibido (doc 01 §UX.md, principio de comunicación de procesos asíncronos).

---

## 6.30 Matriz de tamaños - resumen transversal

| Tamaño | Botón (alto) | Input (alto) | Ícono | Uso |
|---|---|---|---|---|
| `sm` | 32px | 32px | 16px | Tablas densas, toolbars |
| `md` | 40px | 40px | 20px | Por defecto, uso profesional |
| `lg` | 48px | 48px | 24px | Flujos de paciente/familiar, emergencia |

## 6.31 Responsive transversal de componentes

- Modales `sm`/`md` → en mobile se convierten en **bottom sheet** de ancho completo (no un modal centrado angosto), más natural para pulgar.
- Dropdown/Menu → en mobile, ítems con altura mínima 44px (vs. 36px en desktop), por precisión táctil.
- Tabs → scroll horizontal en mobile, nunca wrap a dos líneas.
- Sidebar → drawer en mobile/tablet portrait (ver doc 07).
