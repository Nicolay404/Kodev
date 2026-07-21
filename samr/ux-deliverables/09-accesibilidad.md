# 09 — Accesibilidad
## SAMR — Sistema de Atención Médica Remota

> Estándar objetivo: **WCAG 2.2 Nivel AA** (el rol UX del proyecto exige 2.1 AA como piso — este documento sube el estándar a 2.2 AA, que lo incluye y añade criterios más estrictos sobre foco y objetivos táctiles, coherentes con lo ya exigido). Accesibilidad es **requisito funcional**, no checklist final — se diseña con ella desde el primer wireframe (doc 04), no se "agrega" al final.

---

## 9.1 Contraste

| Contexto | Ratio mínimo | Aplicación en SAMR |
|---|---|---|
| Texto normal (<18px o <14px bold) | 4.5:1 | Todo el texto de cuerpo del sistema (doc 05 §5.3) |
| Texto grande (≥18px o ≥14px bold) | 3:1 | Títulos, texto de badges grandes |
| **Alertas críticas** | **7:1** | Todo texto dentro de `alerta-critico` y del badge de nivel "Crítico" — supera el mínimo AA deliberadamente |
| Componentes UI no textuales (bordes de input, ícono standalone) | 3:1 contra el fondo adyacente | Bordes de foco, iconografía funcional |
| Estados de foco (WCAG 2.2 — Focus Not Obscured / Focus Appearance) | El indicador de foco debe tener ≥3:1 contra los colores adyacentes y un área mínima equivalente a un borde de 2px alrededor del componente | Anillo de foco `teal-600` 2px, offset 2px (doc 06) |

**Verificación obligatoria antes de merge**: cada nueva pantalla se corre por **axe DevTools** y **Lighthouse Accessibility** (mínimo 95/100). Ningún par de color definido en el doc 05 se considera aprobado hasta pasar esta verificación automatizada — los valores del doc 05 son el punto de partida de diseño, no la certificación final.

## 9.2 Tamaño de fuente

- Mínimo absoluto: **16px** (`text-base`) para cualquier texto de cuerpo dirigido a paciente/familiar — nunca `text-sm` (14px) como tamaño principal en esos flujos.
- Texto de alerta crítica: mínimo **18px** (`text-critico`, doc 05).
- El usuario puede aumentar el tamaño de texto del sistema hasta 200% (`/app/configuracion/accesibilidad`) sin pérdida de funcionalidad ni recorte de contenido (WCAG 1.4.4 Resize Text) — el layout debe reflow, no solo escalar con overflow oculto.
- Ningún tamaño de fuente se fija en unidades absolutas (`px`) en el CSS final — se usan `rem` para respetar la configuración de tamaño de fuente del navegador/SO del usuario.

## 9.3 Navegación por teclado

**Regla absoluta (heredada de `UX.md`)**: ningún flujo depende exclusivamente de mouse/touch — incluidos teleconsulta y reporte de emergencia.

| Flujo | Ruta de teclado esperada |
|---|---|
| Login/Registro | Tab avanza campo a campo en orden visual; Enter en el último campo envía el formulario |
| Chat de solicitud | Tab lleva del input de mensaje a las chips de respuesta rápida (si existen) antes que al botón enviar; Enter envía el mensaje sin necesitar clic |
| Cola de casos | Tab navega card por card; Enter/Space sobre una card abre el detalle (igual que un clic) |
| Teleconsulta | Todos los controles (mic, cámara, chat, colgar) alcanzables por Tab, con atajos de teclado documentados en tooltip (ej. `M` mute) — colgar **nunca** es alcanzable por un solo Enter accidental sin foco explícito previo en ese control |
| Modal de confirmación destructiva | Foco inicial en "Cancelar" (nunca en la acción destructiva), `Escape` cierra como Cancelar |
| Emergencia activa | El botón de llamada telefónica de respaldo es el primer elemento tabbable de toda la pantalla |

Orden de tabulación siempre coincide con el orden visual (top-to-bottom, left-to-right) — ningún `tabindex` positivo que rompa ese orden natural.

## 9.4 ARIA — patrones por componente

| Componente | Patrón ARIA |
|---|---|
| Chat de solicitud | Región del hilo de mensajes con `role="log"` y `aria-live="polite"` — nuevos mensajes del bot se anuncian sin interrumpir lo que el usuario esté haciendo |
| Alerta crítica / badge nivel crítico | `role="alert"` + `aria-live="assertive"` (mandato explícito de `UX.md`) — se anuncia de inmediato sin que el usuario deba enfocarlo manualmente |
| Alerta alta/moderada/leve | `aria-live="polite"` — se anuncia sin interrumpir el flujo de lectura actual |
| Stepper de estado de solicitud | `aria-current="step"` en el paso activo |
| Modal | `role="dialog"` + `aria-modal="true"` + `aria-labelledby` apuntando al título (resuelto por Radix `Dialog` por defecto) |
| Toast | `role="status"` (success/info) o `role="alert"` (error) según severidad |
| Tabs | `role="tablist"`/`role="tab"`/`role="tabpanel"` con `aria-selected` (resuelto por Radix `Tabs`) |
| Tabla | Encabezados con `scope="col"`, tabla con `<caption>` visualmente oculto (`sr-only`) describiendo su propósito para lectores de pantalla |
| Skeleton loader | `aria-busy="true"` en el contenedor mientras carga, `aria-live="polite"` con texto oculto ("Cargando casos…") — el skeleton visual no comunica nada a un lector de pantalla por sí mismo |
| Video de teleconsulta | Controles con `aria-label` explícito por ícono ("Silenciar micrófono", no solo el ícono) |
| Guía de primeros auxilios (paso a paso) | Cada paso con `aria-live="polite"` al cambiar, foco programático movido al nuevo paso al avanzar |

## 9.5 Estados de foco

- Visible **siempre** que la navegación sea por teclado (`:focus-visible`, no `:focus` genérico — evita el anillo en clics de mouse donde no aporta valor, pero nunca se suprime vía `outline: none` sin reemplazo).
- Especificación: anillo `2px solid teal-600` + `offset 2px` (doc 05/06) — cumple WCAG 2.2 criterio 2.4.11 (Focus Not Obscured) al no quedar nunca tapado por elementos sticky (navbar, footer fijo de formulario).
- En modo oscuro, el anillo usa `teal-400` para mantener el contraste de 3:1 contra fondos oscuros.

## 9.6 Lectores de pantalla

- Testeo obligatorio con **NVDA** (Windows, gratuito) y **VoiceOver** (macOS/iOS) antes de dar por cerrado cualquier flujo crítico (autenticación, solicitud, emergencia, teleconsulta).
- Todo ícono funcional sin texto visible lleva `aria-label`; todo ícono puramente decorativo lleva `aria-hidden="true"`.
- Las imágenes ilustrativas de estados vacíos (doc 05 §5.8) llevan `alt=""` (decorativas) — el mensaje textual que las acompaña ya comunica el contenido, no se duplica en el `alt`.
- El orden de lectura (DOM order) coincide siempre con el orden visual — ningún reposicionamiento vía CSS (`order`, `grid-area`) que desalinee ambos sin ajustar también el DOM.

## 9.7 Áreas táctiles

Mínimo **44×44px** en todo elemento interactivo (WCAG 2.5.8 Target Size Minimum, nivel AA en 2.2) — sin excepción en flujos de paciente/familiar/paramédico (doc 06 §6.30, doc 07 §7.12). Separación mínima de 8px entre objetivos táctiles adyacentes para evitar toques accidentales, crítico en `P-Emergencia-Activa` donde un toque erróneo no puede tener consecuencia grave (los controles irreversibles ahí están deliberadamente espaciados y de mayor tamaño que el mínimo).

## 9.8 Movimiento y animación

- Toda animación respeta `prefers-reduced-motion: reduce` (detalle completo en doc 08).
- Ninguna animación parpadea a una frecuencia entre 2Hz y 55Hz en un área mayor al umbral de seguridad (WCAG 2.3.1, riesgo de convulsiones) — el pulso de urgencia crítica está deliberadamente fijado en **1Hz**, muy por debajo del umbral de riesgo, y así queda documentado como decisión de diseño explícita, no casual.

## 9.9 Formularios accesibles

- Todo `<input>` tiene un `<label>` asociado (`htmlFor`/`id`), nunca solo un placeholder como identificador de campo (el placeholder desaparece al escribir, un usuario de lector de pantalla o con memoria de trabajo reducida lo pierde).
- Mensajes de error asociados al campo vía `aria-describedby`, y el campo marcado con `aria-invalid="true"` mientras el error persiste.
- Agrupaciones de radio/checkbox relacionados envueltas en `<fieldset>` + `<legend>` (ej. los 3 consentimientos LOPDP del registro).

## 9.10 Independencia de color

Todo estado que hoy se comunica por color en este sistema (doc 05/06) lleva un segundo canal — ícono, texto o patrón — sin excepción. Verificación específica: simular deuteranopía/protanopía/tritanopía (herramienta: extensión "Colorblindly" o el emulador de DevTools de Chrome) sobre `P-Cola-Casos`, `P-Emergencia-Activa` y el badge de nivel de riesgo — estas tres superficies son las de mayor consecuencia clínica si el color falla como único canal.

## 9.11 Checklist de verificación por herramienta

| Herramienta | Qué verifica | Cuándo |
|---|---|---|
| axe DevTools | Violaciones WCAG automatizables (contraste, labels, roles ARIA) | Cada PR de una pantalla nueva |
| Lighthouse Accessibility | Score general + oportunidades | Cada PR |
| Navegación solo-teclado manual | Flujos completos sin mouse | Antes de cerrar cada historia de usuario |
| NVDA / VoiceOver | Comprensión real del contenido leído en voz | Flujos críticos (auth, solicitud, emergencia, teleconsulta) antes de release |
| Emulador de daltonismo | Independencia de color en superficies de urgencia | Antes de aprobar `P-Cola-Casos` y `P-Emergencia-Activa` |
| Zoom de navegador a 200% | Reflow sin pérdida de contenido/función | Cada pantalla nueva |
