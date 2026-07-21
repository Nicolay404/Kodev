# SAMR - UX/UI
## Rama `ux/design-prototypes`

> Accesibilidad, jerarquía visual de urgencia y sistema de diseño. Para el stack técnico que implementa estos lineamientos ver `ui/frontend-app`.

---

# 1. Accesibilidad - Requisito Funcional, no Estético

**WCAG 2.1 AA** se trata como requisito funcional del sistema, no como acabado visual opcional, porque SAMR atiende a pacientes en situaciones de estrés, adultos mayores, y personas con distintas capacidades:

- **Contraste mínimo 4.5:1** en texto normal, **7:1** en alertas críticas.
- **Navegación completa por teclado** - ningún flujo (incluida la teleconsulta y el reporte de una emergencia) puede depender exclusivamente del mouse/touch.
- **`aria-live="assertive"`** en alertas de nivel crítico, para que lectores de pantalla las anuncien de inmediato sin que el usuario tenga que enfocarlas manualmente.
- **Áreas táctiles mínimas de 44×44px** - crítico para adultos mayores o personas con temblor/movilidad reducida usando el bot o reportando síntomas desde el celular.

---

# 2. Jerarquía de Urgencia - Semiótica Redundante

**Nunca solo color.** Cada nivel de riesgo se comunica con **color + ícono + tipografía** simultáneamente, para que la información llegue igual a una persona con daltonismo:

| Nivel | Color | Comportamiento adicional |
|---|---|---|
| Crítico | Rojo | Pulso a 1Hz (parpadeo sutil, no epiléptico) |
| Alto | Naranja | - |
| Moderado | Amarillo | - |
| Leve | Verde | - |

Esta jerarquía debe ser consistente en **todo** el sistema: el mismo código de color/ícono para "crítico" en el chatbot, en el dashboard del profesional y en la notificación push.

---

# 3. Comunicación de Procesos Asíncronos

Los procesos que corren en segundo plano (evaluación de riesgo con IA, matching paciente-profesional) **no deben mostrarse con un spinner genérico ni una barra de progreso falsa** - ambos aumentan la ansiedad percibida en un momento de urgencia médica, precisamente porque no comunican nada real sobre qué está pasando.

En su lugar:
- **Mensajes de progreso contextuales** - ej. "Evaluando el nivel de urgencia de tus síntomas..." en vez de un `%` inventado.
- **Skeleton loaders** que anticipan la forma real del contenido que va a aparecer, reduciendo el "salto" visual cuando llega la respuesta.

---

# 4. Sistema de Diseño

- **Radix UI** (headless, accesible por defecto) - se elige explícitamente para no tener que reconstruir accesibilidad desde cero en cada componente (focus trap, roles ARIA, manejo de teclado ya vienen resueltos).
- **Tailwind CSS** como capa utilitaria sobre Radix, para mantener consistencia visual sin duplicar estilos por componente.

---

# 5. Checklist de Revisión de Prototipos

- [ ] Todo estado crítico tiene color + ícono + texto, nunca solo color.
- [ ] Todo flujo probado con navegación por teclado (Tab/Enter/Escape) sin usar el mouse.
- [ ] Contraste verificado con una herramienta automática (ej. axe, Lighthouse) antes de aprobar el prototipo.
- [ ] Ningún spinner genérico en procesos que tarden más de ~2 segundos - usar mensaje contextual o skeleton.
- [ ] Áreas táctiles medidas en el prototipo (no solo "se ven grandes") - mínimo 44×44px.

---
*Ver también: `ui/frontend-app` (implementación técnica de estos lineamientos en React/Tailwind/Radix).*
