# 08 - Microinteracciones
## SAMR - Sistema de Atención Médica Remota

> Implementación con **Framer Motion** (definido en la arquitectura v4). Regla maestra: toda animación debe respetar `prefers-reduced-motion: reduce` - en ese caso se sustituye por un cambio de estado instantáneo (opacidad/posición final directa, sin transición), nunca se elimina el feedback, solo el movimiento (ver doc 09). Ninguna animación decorativa supera los 400ms - SAMR no es un producto de entretenimiento, la velocidad percibida es parte de la confianza clínica.

---

## 8.1 Curvas de easing (tokens)

| Token | Curva CSS / Framer Motion | Uso |
|---|---|---|
| `ease-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` | Transiciones generales (la mayoría de los casos) |
| `ease-entrance` | `cubic-bezier(0, 0, 0.2, 1)` | Elementos que aparecen (modales, toasts, dropdowns) |
| `ease-exit` | `cubic-bezier(0.4, 0, 1, 1)` | Elementos que desaparecen - salida más rápida que la entrada |
| `ease-spring-soft` | `spring(stiffness: 300, damping: 30)` | Switches, checkboxes, feedback táctil de botón |

## 8.2 Duraciones estándar

| Token | Duración | Uso |
|---|---|---|
| `duration-instant` | 100ms | Hover de color, cambios de estado de foco |
| `duration-fast` | 150ms | Tabs, accordion, toggle de estado |
| `duration-base` | 200ms | Aparición de dropdown/tooltip, hover de card (shadow) |
| `duration-medium` | 300ms | Modal, drawer, bottom sheet |
| `duration-slow` | 400ms | Transición de página completa (uso mínimo, solo en cambios de contexto grandes como abrir la sala de emergencia) |

**Regla**: nunca una duración mayor a 400ms fuera del pulso de urgencia crítica (que tiene su propio ciclo definido en 8.6).

## 8.3 Hover

| Elemento | Efecto | Duración |
|---|---|---|
| Botón primario/secundario | Cambio de fondo (doc 06.1) | `duration-instant` |
| Card interactiva | Elevación de `shadow-sm`→`shadow-md` + `translateY(-2px)` | `duration-base` |
| Fila de tabla | Fondo `gray-50` | `duration-instant` |
| Link | Subrayado aparece | `duration-instant` |
| Ícono de acción en toolbar | Fondo circular `gray-100` aparece detrás del ícono | `duration-instant` |

## 8.4 Click / Active

| Elemento | Efecto |
|---|---|
| Botón | `scale(0.98)` durante `duration-instant`, vuelve a `scale(1)` al soltar - feedback táctil inmediato |
| Checkbox/Radio | Ligero "pop": `scale(1.1)` → `scale(1)` en `ease-spring-soft` al marcarse |
| Card clickeable | `scale(0.99)` sutil, evita sensación de "no registró el clic" |

## 8.5 Scroll

- **Reveal progresivo**: solo en pantallas de contenido largo no crítico (ej. `/app/ayuda`, landing de auth) - elementos entran con `opacity 0→1` + `translateY(8px→0)` al entrar en viewport, `duration-base`, sin repetir la animación si el usuario vuelve a hacer scroll hacia arriba y abajo (se anima una sola vez por sesión de scroll).
- **Prohibido en pantallas operativas** (`/app/casos`, `/app/auditoria`, cualquier tabla): el contenido de trabajo aparece instantáneamente - animar cada fila de una tabla larga genera fatiga y ralentiza percibidamente el escaneo de información.
- **Sticky header de tabla**: transición de sombra (`shadow-none`→`shadow-sm`) al despegarse durante scroll, `duration-instant`.

## 8.6 Pulso de urgencia crítica

Único patrón de animación en loop continuo del sistema, reservado exclusivamente para el nivel **Crítico** (doc 05 §5.1):
- Ciclo: `opacity 1 → 0.85 → 1`, frecuencia **1Hz** (1000ms por ciclo completo), `ease-standard`.
- Aplica al badge de nivel de riesgo y al borde de `card-urgencia` cuando el nivel es crítico - nunca al texto de cuerpo (mantener legibilidad constante).
- Se detiene automáticamente si `prefers-reduced-motion: reduce` está activo, sustituido por un borde estático de mayor grosor (4px en vez de pulso) para conservar la señal de urgencia sin movimiento.

## 8.7 Aparición (entrada)

| Componente | Efecto | Duración | Curva |
|---|---|---|---|
| Modal | Overlay `opacity 0→1` + contenido `opacity 0→1` + `scale(0.96→1)` | `duration-medium` | `ease-entrance` |
| Bottom sheet (mobile) | `translateY(100%→0)` | `duration-medium` | `ease-entrance` |
| Toast | `translateX(24px→0)` + `opacity 0→1` (desde la derecha en desktop) / `translateY(-24px→0)` (desde arriba en mobile) | `duration-base` | `ease-entrance` |
| Dropdown/Tooltip | `opacity 0→1` + `scale(0.96→1)`, origen desde el punto de anclaje (`transform-origin`) | `duration-base` | `ease-entrance` |
| Skeleton → Contenido real | Cross-fade `opacity`, nunca un salto abrupto | `duration-base` | `ease-standard` |

## 8.8 Desaparición (salida)

Todas las salidas usan `ease-exit` y duración igual o menor a su entrada correspondiente (una interfaz debe sentirse más rápida al cerrarse que al abrirse - reduce percepción de bloqueo). Excepción: el toast de error crítico no se anima al desaparecer automáticamente porque **no desaparece automáticamente** (doc 06.14) - solo se anima su cierre manual.

## 8.9 Transición entre pantallas (routing)

Cross-fade simple `opacity 0→1`, `duration-fast` (150ms) - sin transiciones de "deslizamiento" tipo app nativa, que en un contexto de datos clínicos densos generan más distracción que valor. Excepción: la entrada a `P-Emergencia-Activa` usa una transición ligeramente más marcada (`duration-slow`, con el color de urgencia expandiéndose desde arriba) - es la única transición de página que debe *sentirse* como un cambio de contexto importante.

## 8.10 Feedback visual de formularios

| Evento | Feedback |
|---|---|
| Validación exitosa de campo (en tiempo real) | Ícono de check aparece con `scale(0→1)`, `duration-instant`, color `success-600` |
| Error de validación | El campo tiembla sutilmente (`translateX: -4px, 4px, -2px, 0`, ~200ms total) **solo la primera vez que aparece el error**, no en cada re-validación - evita ruido repetitivo |
| Envío de formulario en proceso | Botón entra en estado `loading` (doc 06.1), inputs se deshabilitan con opacidad reducida, sin animación adicional |
| Guardado automático (borrador) | Micro-indicador de texto "Guardado" con fade in/out de 2s total, esquina del formulario, no interrumpe |

## 8.11 Skeleton shimmer

Animación de fondo en gradiente que se desplaza horizontalmente: `background-position` de `-200% 0` a `200% 0` en loop continuo, `duration: 1500ms`, `ease-standard`, `linear` en la repetición (sin pausa entre ciclos). Se detiene y sustituye por opacidad estática pulsante muy sutil si `prefers-reduced-motion: reduce`.

## 8.12 Íconos con estado

- Chevron de Accordion/Select: `rotate(0deg → 180deg)`, `duration-fast`.
- Ícono de "copiar al portapapeles": cambia a check por 1.5s tras el clic, luego vuelve a su ícono original con cross-fade.
- Ícono de conexión (Navbar): transición de color (verde→ámbar→rojo) según calidad de conexión, `duration-base`, nunca parpadea salvo en estado "reconectando" (ver doc 11), donde usa una opacidad pulsante suave (no el pulso de urgencia, que está reservado exclusivamente para riesgo clínico crítico).

## 8.13 Principio general

Ninguna microinteracción es puramente decorativa. Cada una de las especificadas arriba comunica: **estado** (¿cambió algo?), **jerarquía** (¿qué es más importante ahora mismo?) o **confianza** (¿el sistema registró mi acción?). Si una animación propuesta durante el desarrollo no responde a una de estas tres preguntas, no se implementa.
