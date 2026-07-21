# 05 — Diseño Visual (UI)
## SAMR — Sistema de Atención Médica Remota

> Estilo visual objetivo: **"calma clínica"** — confiable, legible primero, bajo ruido visual, whitespace generoso, cero decoración gratuita. El color de urgencia se reserva *exclusivamente* para el sistema de urgencia (doc 09/06): si el rojo aparece, siempre significa lo mismo. Todos los valores de contraste indicados son de diseño; **deben verificarse con axe/Lighthouse antes de aprobar cualquier pantalla** (ver checklist doc 13) — son el punto de partida, no el reemplazo de la verificación automática.

---

## 5.1 Paleta de colores

### Primario — `samr-teal` (marca, confianza clínica)

| Token | Hex | Uso |
|---|---|---|
| `teal-50` | `#EFFCFB` | Fondos sutiles, hover de filas |
| `teal-100` | `#D7F7F3` | Fondos de badges suaves |
| `teal-200` | `#AEEEE8` | Bordes decorativos |
| `teal-300` | `#78DFD6` | Iconografía secundaria |
| `teal-400` | `#3EC8BC` | Estados hover de elementos claros |
| `teal-500` | `#1FA89C` | **Color de marca por defecto** |
| `teal-600` | `#148075` | **Primario accionable** — botones primarios, links, foco |
| `teal-700` | `#0F6259` | Hover/active de botón primario |
| `teal-800` | `#0B4A43` | Texto sobre fondos claros de marca |
| `teal-900` | `#082F2B` | Texto de máximo énfasis en modo claro |

### Secundario — `samr-indigo` (acciones secundarias, elementos informativos no urgentes)

| Token | Hex | Uso |
|---|---|---|
| `indigo-500` | `#6366F1` | Acentos secundarios |
| `indigo-600` | `#4F46E5` | Botones secundarios, links dentro de contenido |
| `indigo-700` | `#4338CA` | Hover/active |

### Semánticos

| Token | Hex | Uso |
|---|---|---|
| `success-600` | `#16A34A` | Fondos/iconos de éxito |
| `success-700` | `#15803D` | Texto de éxito sobre blanco, botones de confirmación |
| `error-600` | `#DC2626` | Fondos/iconos de error |
| `error-700` | `#B91C1C` | Texto de error sobre blanco |
| `warning-500` | `#F59E0B` | Fondos de advertencia (con texto oscuro `neutral-900` encima) |
| `warning-700` | `#B45309` | Texto de advertencia sobre blanco |
| `info-600` | `#2563EB` | Fondos/iconos informativos |
| `info-700` | `#1D4ED8` | Texto informativo sobre blanco |

### Escala de urgencia clínica (semiótica redundante — nunca solo color, ver doc 09)

| Nivel | Fondo | Texto sobre fondo | Ícono | Comportamiento |
|---|---|---|---|---|
| **Crítico** | `#B91C1C` (`red-700`) | Blanco `#FFFFFF` | Triángulo de alerta relleno | Pulso 1Hz (ver doc 08) |
| **Alto** | `#C2410C` (`orange-700`) | Blanco `#FFFFFF` | Triángulo de alerta | Estático |
| **Moderado** | `#F59E0B` (`amber-500`) | Oscuro `#1C1917` (`neutral-900`) | Círculo con signo | Estático |
| **Leve** | `#15803D` (`green-700`) | Blanco `#FFFFFF` | Check circular | Estático |

Esta paleta debe ser **idéntica** en el chatbot, el dashboard clínico y las notificaciones push — es el contrato visual más importante del sistema (RF/NFR de jerarquía de urgencia).

**Nota de implementación** (ver [00](00-alineacion-backend.md) §0.3 M2): existen dos escalas de 4 niveles distintas en el backend — `Evaluacion.nivel_riesgo` (`critico/alto/medio/bajo`, usada en M2, usa esta tabla completa) y `Alert.severity` de `monitoring-service` (`critical/high/medium/low`), pero en el código actual **toda alerta generada automáticamente se crea siempre con `severity="critical"`** — los otros 3 niveles del choice nunca se producen en la práctica. La paleta se mantiene completa (es correcta para `nivel_riesgo` y forward-compatible para `Alert`), pero el frontend no debe esperar ver hoy un badge de alerta IoT en naranja/amarillo/verde — solo rojo.

### Neutrales — `samr-gray`

| Token | Hex | Uso |
|---|---|---|
| `gray-50` | `#F8FAFC` | Fondo de página (modo claro) — **no blanco puro**, reduce fatiga visual |
| `gray-100` | `#F1F5F9` | Fondo de superficies secundarias |
| `gray-200` | `#E2E8F0` | Bordes por defecto |
| `gray-300` | `#CBD5E1` | Bordes de énfasis, divisores |
| `gray-400` | `#94A3B8` | Texto deshabilitado, placeholder |
| `gray-500` | `#64748B` | Texto secundario |
| `gray-600` | `#475569` | Texto secundario de énfasis |
| `gray-700` | `#334155` | Texto de cuerpo |
| `gray-800` | `#1E293B` | Texto de encabezados |
| `gray-900` | `#0F172A` | Texto de máximo contraste / fondo modo oscuro |

## 5.2 Modo claro / Modo oscuro — tokens semánticos

| Token semántico | Modo claro | Modo oscuro |
|---|---|---|
| `bg-page` | `gray-50` `#F8FAFC` | `gray-900` `#0F172A` |
| `bg-surface` | `#FFFFFF` | `#1E293B` (`gray-800`) |
| `bg-surface-elevated` | `#FFFFFF` + sombra | `#1E293B` + borde `gray-700` |
| `border-default` | `gray-200` | `gray-700` `#334155` |
| `text-primary` | `gray-900` | `gray-50` `#F8FAFC` |
| `text-secondary` | `gray-600` | `gray-400` `#94A3B8` |
| `text-disabled` | `gray-400` | `gray-600` |
| `primary-action` | `teal-600` | `teal-400` `#3EC8BC` (más claro para mantener contraste sobre fondo oscuro) |
| `critico-bg` | `red-700` | `red-500` `#EF4444` (ajustado para contraste sobre oscuro) |
| `alto-bg` | `orange-700` | `orange-500` `#F97316` |
| `moderado-bg` | `amber-500` | `amber-400` `#FBBF24` |
| `leve-bg` | `green-700` | `green-500` `#22C55E` |

**Regla de modo oscuro**: los colores semánticos y de urgencia se aclaran un paso en la escala respecto al modo claro (700→500, 500→400) para mantener el ratio de contraste contra fondos oscuros — nunca se reutiliza el mismo hex en ambos modos.

## 5.3 Tipografía

**Familia tipográfica: Inter** (+ fallback `system-ui, -apple-system, sans-serif`).
Justificación: alta legibilidad en pantalla a tamaños pequeños, x-height generoso (crítico para adultos mayores y lectura bajo estrés), soporte completo de acentos/ñ para español, variable font (rendimiento), sin connotación "corporativa fría" ni "juguetona" — neutral y clínica. Se usa la misma familia para títulos y cuerpo (sin fuente decorativa secundaria) para minimizar ruido visual.

### Escala tipográfica (base 16px, ratio ~1.25)

| Token | Tamaño | Line-height | Peso por defecto | Uso |
|---|---|---|---|---|
| `text-xs` | 12px | 16px | 400 | Metadatos, timestamps, labels de badges |
| `text-sm` | 14px | 20px | 400 | Texto secundario, ayudas de formulario |
| `text-base` | 16px | 24px | 400 | **Cuerpo por defecto — mínimo absoluto para texto dirigido a paciente** |
| `text-lg` | 18px | 28px | 500 | Texto de énfasis, subtítulos |
| `text-xl` | 20px | 28px | 600 | Títulos de sección |
| `text-2xl` | 24px | 32px | 600 | Títulos de página |
| `text-3xl` | 30px | 38px | 700 | Encabezados de pantallas de alto impacto (auth, emergencia) |
| `text-4xl` | 36px | 44px | 700 | Landing / estados vacíos ilustrados |
| `text-critico` | 18px mínimo | 28px | 600 | **Todo texto de alerta crítica** — nunca por debajo de 18px |

Pesos disponibles: 400 (regular), 500 (medium), 600 (semibold), 700 (bold). No se usa 300 (light) — reduce legibilidad para baja visión.

## 5.4 Sistema de espaciado

Grid base de **8px**, con un paso intermedio de 4px solo para ajustes finos (íconos dentro de botones pequeños).

| Token | Valor | Uso típico |
|---|---|---|
| `space-1` | 4px | Separación entre ícono y texto en línea |
| `space-2` | 8px | Padding interno de chips/badges |
| `space-3` | 12px | Padding interno de inputs |
| `space-4` | 16px | Padding interno de cards, gap por defecto |
| `space-5` | 20px | — |
| `space-6` | 24px | Padding de secciones dentro de una página |
| `space-8` | 32px | Separación entre bloques de contenido |
| `space-10` | 40px | — |
| `space-12` | 48px | Separación entre secciones mayores |
| `space-16` | 64px | Márgenes de layout en desktop |
| `space-20` | 80px | — |
| `space-24` | 96px | Espaciado de landing/hero |

## 5.5 Bordes y radios

| Token | Valor | Uso |
|---|---|---|
| `radius-sm` | 4px | Chips, badges pequeños |
| `radius-md` | 8px | Botones, inputs, selects |
| `radius-lg` | 12px | Cards, modales |
| `radius-xl` | 16px | Contenedores de alto nivel (paneles de dashboard) |
| `radius-full` | 9999px | Avatares, pills, switches |
| `border-width-default` | 1px | Bordes estándar |
| `border-width-focus` | 2px | Anillo de foco (accesibilidad) |

## 5.6 Sombras y elevación

| Token | Valor CSS | Uso |
|---|---|---|
| `shadow-sm` | `0 1px 2px rgba(15,23,42,0.06)` | Cards en reposo |
| `shadow-md` | `0 4px 6px rgba(15,23,42,0.08)` | Cards hover, dropdowns |
| `shadow-lg` | `0 10px 15px rgba(15,23,42,0.10)` | Popovers, tooltips |
| `shadow-xl` | `0 20px 25px rgba(15,23,42,0.12)` | Modales |
| `shadow-2xl` | `0 25px 50px rgba(15,23,42,0.18)` | Overlay de emergencia (P-Emergencia-Activa) |

En modo oscuro las sombras se sustituyen por un borde `gray-700` de 1px + un halo sutil, ya que las sombras pierden legibilidad sobre fondos oscuros.

## 5.7 Iconografía

- **Librería: Lucide Icons** (open-source, MIT, consistente con el ecosistema Radix, trazo uniforme).
- Grosor de trazo: 1.5px por defecto, 2px en tamaños ≤16px (mejora legibilidad a tamaño pequeño).
- Tamaños estándar: 16px (inline con texto sm), 20px (inline con texto base), 24px (botones, navegación), 32px (estados vacíos, ilustrativo).
- Los íconos de urgencia (crítico/alto/moderado/leve) son siempre **rellenos** (`filled`), no de solo contorno — mejora reconocimiento rápido y contraste.

## 5.8 Ilustraciones

- Estilo: **line-art minimalista**, geométrico, sin rostros humanos hiperrealistas ni fotografías de stock de "médicos sonriendo" (generan desconfianza/artificialidad en contexto clínico real).
- Uso: exclusivamente en estados vacíos, onboarding y pantallas de error (doc 11) — nunca en flujos críticos (emergencia, teleconsulta activa), donde cualquier elemento no funcional es ruido.
- Paleta de ilustraciones: monocromática en `teal-200`/`teal-400` sobre fondo `gray-50`, para no competir con la paleta de urgencia.

## 5.9 Glassmorphism

Uso **restringido y deliberado**: únicamente en chrome de overlay no informativo (barra de controles flotante sobre el video de teleconsulta — cámara/micrófono/colgar). 

**Prohibido explícitamente**: texto de cuerpo, badges de urgencia, o cualquier contenido crítico detrás de un fondo con blur — el desenfoque reduce contraste efectivo y es un riesgo de accesibilidad para baja visión (contradice WCAG 1.4.11).

Especificación cuando se usa: `background: rgba(15,23,42,0.55); backdrop-filter: blur(12px);` sobre superficie oscura, con controles de alto contraste encima (íconos blancos, ≥3:1 contra el fondo desenfocado).

## 5.10 Gradientes

Uso mínimo y decorativo, nunca portador de significado:
- Fondo de pantallas de autenticación (`/login`, `/registro`): gradiente sutil `linear-gradient(180deg, teal-50 0%, gray-50 100%)`.
- Prohibido en botones, badges de urgencia o cualquier elemento donde el color comunique estado — un gradiente diluye el hex exacto que el sistema de contraste valida.

## 5.11 Fondos

- Modo claro: `gray-50` (`#F8FAFC`) como fondo de página — nunca blanco puro (`#FFFFFF`), que genera fatiga visual y halo excesivo en pantallas OLED/alta luminosidad.
- Modo oscuro: `gray-900` (`#0F172A`) — nunca negro puro (`#000000`), que produce halation en texto claro y reduce percepción de profundidad entre superficies.
- Superficies (cards, modales) siempre un tono por encima del fondo de página (`bg-surface` vs `bg-page`), nunca el mismo tono — la jerarquía debe percibirse sin depender solo del borde.

## 5.12 Estilo visual — resumen de principios

1. El color comunica estado funcional (urgencia, éxito, error) — no es decoración.
2. Whitespace generoso por defecto; se comprime únicamente en tablas densas de uso profesional (`/app/casos`, `/app/auditoria`).
3. Una sola familia tipográfica en todo el sistema.
4. Los estados críticos (emergencia) usan más espacio y tamaño de texto que el resto del sistema, nunca menos — la jerarquía de urgencia también es tipográfica, no solo cromática.
5. Ningún elemento visual (ilustración, gradiente, glassmorphism) puede interponerse entre el usuario y la información accionable en un flujo de emergencia.
