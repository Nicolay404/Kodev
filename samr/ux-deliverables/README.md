# SAMR - Paquete de Entregables UX/UI
## Rama `ux/design-prototypes`

> Paquete completo de diseño UX/UI del Sistema de Atención Médica Remota (SAMR), producido para que el equipo de frontend (rama `ui/frontend-app`) pueda implementar la interfaz sin tomar decisiones de diseño por su cuenta.
>
> **Autocontenido**: este paquete no depende de otros documentos del repositorio. Toda referencia a requisitos funcionales (REQ-F), no funcionales (NFR) y casos de uso (CU-001 a CU-004) proviene de la documentación de arquitectura y requisitos de SAMR (`samr_documentacion/`, `logic/core-services:Roles/UX.md`), pero los lineamientos aquí están reescritos en su totalidad para que este paquete se sostenga por sí mismo.
>
> **v1.1 - alineado contra el backend real**: la v1.0 se escribió a partir de la documentación de arquitectura prevista. Esta versión se auditó línea por línea contra el código real de los 13 microservicios (`origin/main:samr/`) y corrige cada punto donde la implementación diverge de lo previsto. **Empieza por el doc [00](00-alineacion-backend.md)** - es la fuente de verdad de qué cambió y por qué.

---

## Índice de documentos

| # | Documento | Contenido |
|---|---|---|
| 00 | [Alineación con el Backend Real](00-alineacion-backend.md) | Auditoría del backend real, brechas críticas, correcciones aplicadas y su justificación |
| 01 | [Estrategia UX](01-estrategia-ux.md) | Objetivos de producto y usuario, propuesta de valor, personas, JTBD, escenarios, user journeys, customer journey |
| 02 | [Arquitectura de la Información](02-arquitectura-informacion.md) | Sitemap completo, jerarquía, navegación, relación entre módulos |
| 03 | [User Flows](03-user-flows.md) | Flujos completos por funcionalidad: happy path, edge cases, errores, estados alternativos |
| 04 | [Wireframes](04-wireframes.md) | Descripción detallada de layout, jerarquía y espaciado de cada pantalla |
| 05 | [Diseño Visual (UI)](05-diseno-visual.md) | Paleta de color, tipografía, espaciado, bordes, sombras, iconografía, modo claro/oscuro |
| 06 | [Design System](06-design-system.md) | Especificación de cada componente: variantes, estados, tamaños |
| 07 | [Responsive Design](07-responsive.md) | Comportamiento por breakpoint: mobile, tablet, laptop, desktop, XL |
| 08 | [Microinteracciones](08-microinteracciones.md) | Animaciones, transiciones, duraciones, curvas de easing |
| 09 | [Accesibilidad](09-accesibilidad.md) | WCAG 2.2 AA aplicado a cada patrón de SAMR |
| 10 | [UX Writing](10-ux-writing.md) | Copy deck completo: botones, errores, confirmaciones, tooltips, placeholders |
| 11 | [Estados del Sistema](11-estados-sistema.md) | Empty, loading, error, offline, success, sin permisos, mantenimiento - por pantalla |
| 12 | [Especificaciones para Frontend](12-especificaciones-frontend.md) | Tokens de diseño, variables CSS, clases Tailwind, naming, estructura de carpetas |
| 13 | [Checklist de Implementación](13-checklist-implementacion.md) | Checklist accionable para dar por terminada la UI |
| 14 | [Recomendaciones UX](14-recomendaciones-ux.md) | Mejoras de usabilidad, conversión, accesibilidad, rendimiento percibido |

---

## Cómo usar este paquete (guía para frontend)

0. Lee **00** primero - sin él, varias pantallas de **04** parecerán completas cuando en realidad dependen de un endpoint que hoy no existe. Cada corrección en 01–14 cita su entrada correspondiente en 00.
1. Sigue con **01** y **02** para entender el "por qué" antes del "cómo" - quién usa SAMR y cómo se organiza la información.
2. **05** y **06** son la fuente de verdad visual: toda pantalla descrita en **04** referencia tokens y componentes definidos ahí. No inventes valores nuevos de color/espaciado/tipografía - si falta uno, es un vacío a señalar, no a improvisar.
3. **03** (User Flows) antecede a **04** (Wireframes): primero la lógica del flujo, después su forma visual.
4. **12** traduce todo lo anterior a algo pegable en código (Tailwind config, CSS variables, estructura de carpetas React).
5. **13** es el criterio de aceptación final - ninguna pantalla se da por terminada sin pasar ese checklist.

## Supuestos declarados

Este paquete se basa en la documentación de requisitos y arquitectura de SAMR (20 RF, 38 RNF, CU-001 a CU-004, arquitectura de microservicios v4, stack React 18 + TypeScript + Vite + Zustand + Radix UI + Tailwind CSS). Donde esa documentación no especifica una decisión de diseño, se declaró un supuesto razonable explícitamente en el documento correspondiente, marcado como **[SUPUESTO]**.

---
*Versión 1.0 - Documento vivo: cualquier decisión de diseño no cubierta aquí debe agregarse a este paquete, no resolverse ad hoc en el código.*
