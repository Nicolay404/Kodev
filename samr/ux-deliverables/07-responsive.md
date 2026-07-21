# 07 - Responsive Design
## SAMR - Sistema de Atención Médica Remota

> Enfoque **mobile-first** para todo lo dirigido a Paciente/Familiar/Paramédico (dispositivo dominante: smartphone, a menudo bajo estrés o en campo) y **desktop-first con degradación mobile funcional** (no solo visual) para lo dirigido a Profesional/Admin/DPD (dispositivo dominante: laptop/desktop, pero deben poder operar de emergencia desde un celular).

---

## 7.1 Breakpoints

| Nombre | Rango | Alias Tailwind | Dispositivo típico |
|---|---|---|---|
| Mobile | 0–767px | `base` → `md` | Smartphone |
| Tablet | 768–1023px | `md` → `lg` | Tablet, smartphone grande en horizontal |
| Laptop | 1024–1279px | `lg` → `xl` | Laptop estándar |
| Desktop | 1280–1535px | `xl` → `2xl` | Monitor de oficina |
| Monitores grandes | ≥1536px | `2xl` | Monitor ultrawide, doble monitor (uso clínico intensivo) |

---

## 7.2 Navegación

| Breakpoint | Comportamiento |
|---|---|
| Mobile | Sidebar oculta por defecto → **drawer** activado desde ícono hamburguesa en Navbar, overlay a pantalla completa al abrir, cierra con swipe o tap fuera. Navbar reduce breadcrumb (solo "← Volver"). |
| Tablet | Sidebar colapsada a solo-íconos (72px) por defecto, expandible con tap; contenido usa el espacio ganado. |
| Laptop+ | Sidebar expandida completa (260px) por defecto, colapsable manualmente (preferencia persistida por usuario). |

## 7.3 Grid de contenido

| Breakpoint | Columnas de grid | Comportamiento de layouts 8/12 + 4/12 (doc 04) |
|---|---|---|
| Mobile | 1 columna | Columna lateral pasa **debajo** del contenido principal, nunca se oculta información, solo cambia el orden (contenido crítico primero) |
| Tablet | 1–2 columnas según densidad | Layouts 8/12+4/12 se mantienen si hay ≥768px de ancho útil tras la sidebar; si no, apilan como en mobile |
| Laptop+ | 12 columnas completas | Layout de referencia (doc 04) |

## 7.4 Dashboard

| Breakpoint | Cards de KPI (`card-stat`) | Zona de alerta |
|---|---|---|
| Mobile | 1 columna, scroll vertical | Ancho completo, siempre primera |
| Tablet | 2 columnas | Ancho completo |
| Laptop+ | 3–4 columnas | Ancho completo |

## 7.5 Tablas

Regla explícita (ver doc 06.20): **por debajo de `md` (768px), toda tabla se transforma en una lista de Cards apiladas**, una por fila original, mostrando las 2–3 columnas más relevantes como texto principal/secundario dentro de la card y el resto tras un "Ver más" o dentro del detalle. Nunca scroll horizontal como solución por defecto - el scroll horizontal solo se acepta como fallback temporal si una tabla es inherentemente ancha (ej. comparativa de muchas especialidades) y aun así debe llevar un indicador visual de que hay más contenido a la derecha.

## 7.6 Formularios

| Breakpoint | Comportamiento |
|---|---|
| Mobile | Una columna siempre, inputs `lg` (48px) en flujos de paciente para precisión táctil, teclado nativo apropiado por tipo de campo (`inputmode="numeric"` en dígitos, `type="tel"`, etc.) |
| Tablet+ | Formularios administrativos (`/app/admin/*`) pueden usar 2 columnas; formularios de paciente se mantienen en 1 columna incluso en desktop (consistencia y menor carga cognitiva, doc 04 §4.9) |

## 7.7 Chat de solicitud (P-Chat-Solicitud)

| Breakpoint | Comportamiento |
|---|---|
| Mobile | Pantalla completa, input fijo sobre el teclado virtual (usar `env(safe-area-inset-bottom)` en iOS) |
| Tablet+ | Contenedor centrado `max-width: 720px`, no ocupa todo el ancho - el chat no se beneficia de líneas de texto muy largas |

## 7.8 Teleconsulta (P-Sala-Teleconsulta)

| Breakpoint | Comportamiento |
|---|---|
| Mobile | Video propio del participante remoto a pantalla completa, thumbnail propio pequeño superpuesto; panel de notas/IA (vista Profesional) se oculta tras un botón flotante que abre un bottom sheet, nunca compite con el video por espacio simultáneamente |
| Tablet | Video + panel lateral colapsable (drawer desde la derecha) |
| Laptop+ | Layout de dos columnas fijas (65/35) descrito en doc 04 |

## 7.9 Emergencia activa (P-Emergencia-Activa / P-Emergencia-Paramedico)

Diseñada **mobile-first sin excepción** - es la pantalla con mayor probabilidad de usarse en un smartphone bajo estrés. En breakpoints mayores (tablet/desktop, ej. un familiar viéndolo desde una laptop), el layout simplemente centra el mismo contenido en una columna de `max-width: 640px` - **no se agrega información adicional en pantallas grandes**, la simplicidad es intencional en todos los tamaños.

## 7.10 Modales

| Breakpoint | Comportamiento |
|---|---|
| Mobile | **Bottom sheet** de ancho completo, altura hasta 90% del viewport, con handle visual arriba para cerrar con swipe |
| Tablet+ | Modal centrado clásico (doc 06.25) |

## 7.11 Tipografía responsive

La escala tipográfica (doc 05 §5.3) es la misma en todos los breakpoints - **no se reduce el tamaño de fuente en mobile** (error común que perjudica legibilidad justo donde más se necesita). Lo que cambia es el `line-length` (ancho de línea de texto), limitado a `max-width: 65ch` en cualquier breakpoint para mantener legibilidad óptima.

## 7.12 Zonas táctiles vs. cursor

En breakpoints `mobile`/`tablet` (dispositivos táctiles primarios), todo elemento interactivo respeta el mínimo de 44×44px sin excepción (doc 06 §6.1). En `laptop+`, se permite reducir el tamaño visual de elementos secundarios (ej. íconos de acción en tablas densas) a 32×32px con área de clic ampliada invisible, dado que el cursor de mouse tiene mayor precisión - pero **nunca** en pantallas dirigidas a paciente, donde el estándar de 44×44px se mantiene en todos los breakpoints por consistencia con población de baja motricidad.

## 7.13 Resumen - tabla maestra por página clave

| Página | Mobile | Tablet | Laptop+ |
|---|---|---|---|
| Dashboard | 1 col, alerta arriba | 2 col KPIs | 3–4 col KPIs, 8/12+4/12 |
| Cola de casos | Lista de cards apiladas | Igual | Lista de cards, filtros en fila |
| Chat de solicitud | Pantalla completa | Centrado 720px | Centrado 720px |
| Teleconsulta | Video full + bottom sheet | Video + drawer | Video 65% + panel 35% fijo |
| Emergencia activa | Diseño de referencia (mobile-first) | Mismo contenido centrado | Mismo contenido centrado |
| Tabla (admin/auditoría) | Cards apiladas | Tabla compacta con scroll si necesario | Tabla completa |
| Formulario admin | 1 col | 1–2 col | 2 col |
| Formulario paciente | 1 col, inputs `lg` | 1 col | 1 col (consistencia intencional) |
