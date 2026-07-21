# 13 — Checklist de Implementación
## SAMR — Sistema de Atención Médica Remota

> Ninguna pantalla se marca como "terminada" sin pasar por este checklist completo. Referencia cruzada al documento correspondiente entre paréntesis.

---

## 13.0 Alineación con el backend real (doc 00) — verificar primero

- [ ] Ninguna pantalla marcada 🔴 "Pendiente de backend" en doc 02/04 está conectada a datos simulados/mock en el build que se entrega — o está claramente detrás de un feature flag apagado.
- [ ] Toda pantalla marcada 🟡 "Soportada parcialmente" implementa exactamente la versión reducida descrita (ej. stepper de 2 pasos, matching de 1 acción), no la versión aspiracional original.
- [ ] El rol del usuario se lee del claim JWT `rol` (no `role`) — ver doc 12 §12.7.
- [ ] Las mutaciones (`POST`/`PATCH`/`DELETE`) van directo al gateway, nunca al BFF (que es solo `GET /dashboard/` y `GET /health`).
- [ ] El dashboard de roles distintos a `patient` no depende del BFF — compone sus datos con llamadas directas al gateway (doc 04 §4.3).
- [ ] Ningún componente de UI implica una acción de escritura sobre historial clínico (G12), cambio de contraseña o sesiones activas (G14), o elección de centro en matching (G5) — esas capacidades no existen en el backend actual.
- [ ] Antes de dar por cerrada cualquier historia de usuario que toque un endpoint nuevo, se verificó contra el código real del servicio (no contra la documentación de arquitectura prevista) — la brecha entre "documentado" e "implementado" fue precisamente el motivo de la revisión v1.1 de este paquete.

## 13.1 Diseño visual y tokens (doc 05, 12)

- [ ] No hay ningún color hexadecimal literal en el componente — todo viene de token Tailwind/CSS variable.
- [ ] Tipografía usa exclusivamente Inter (o fallback definido), ninguna fuente ad hoc.
- [ ] Espaciado usa exclusivamente la escala de 8px (o el paso de 4px permitido) — nada de valores arbitrarios (`mt-[13px]`).
- [ ] Radios, sombras y bordes usan los tokens definidos, no valores custom.
- [ ] Modo oscuro implementado y verificado visualmente (no solo "se ve" — verificar contraste real en ambos modos).
- [ ] Ningún gradiente ni glassmorphism sobre texto de cuerpo o badges de urgencia.

## 13.2 Componentes del Design System (doc 06)

- [ ] El componente usa la primitiva Radix correspondiente si existe (no se reinventó comportamiento ya resuelto).
- [ ] Todos los estados obligatorios están implementados: default, hover, focus, active, disabled, y error/success si aplica.
- [ ] El componente respeta el tamaño mínimo táctil de 44×44px si es interactivo y está en un flujo de paciente/familiar/paramédico.
- [ ] El componente es reutilizado desde `design-system/`, no duplicado dentro de `features/`.

## 13.3 Responsive (doc 07)

- [ ] Verificado en los 5 breakpoints: mobile, tablet, laptop, desktop, monitor grande.
- [ ] Ninguna tabla tiene scroll horizontal como única solución en mobile — se transforma en lista de cards.
- [ ] El tamaño de fuente no se reduce en mobile respecto a desktop.
- [ ] Sidebar/navegación se comporta según el patrón definido por breakpoint (drawer / colapsada / expandida).
- [ ] Modales se convierten en bottom sheet en mobile.

## 13.4 Accesibilidad (doc 09)

- [ ] Contraste verificado con axe DevTools/Lighthouse — mínimo 4.5:1 texto normal, 7:1 alertas críticas, 3:1 componentes no textuales.
- [ ] Flujo completo navegable solo con teclado (Tab/Enter/Escape/Space), sin usar mouse.
- [ ] Todo ícono funcional sin texto visible tiene `aria-label`; todo ícono decorativo tiene `aria-hidden="true"`.
- [ ] Alertas críticas usan `role="alert"` + `aria-live="assertive"`; alertas no críticas usan `aria-live="polite"`.
- [ ] Foco visible (`:focus-visible`) en todo elemento interactivo, con el anillo de 2px definido, nunca `outline: none` sin reemplazo.
- [ ] Todo input tiene `<label>` asociado — el placeholder nunca es el único identificador.
- [ ] Probado con NVDA o VoiceOver si el flujo es crítico (auth, solicitud, emergencia, teleconsulta).
- [ ] Ninguna información se comunica solo por color — verificado con emulador de daltonismo en superficies de urgencia.
- [ ] `prefers-reduced-motion: reduce` respetado — animaciones sustituidas por cambios instantáneos.
- [ ] Zoom a 200% probado sin pérdida de contenido ni función.

## 13.5 Microinteracciones (doc 08)

- [ ] Duraciones y curvas de easing usan los tokens definidos, no valores arbitrarios.
- [ ] Ninguna animación decorativa supera 400ms.
- [ ] El pulso de urgencia crítica está a 1Hz exacto y se detiene con `prefers-reduced-motion`.
- [ ] Ninguna animación de "reveal al hacer scroll" está presente en pantallas operativas (tablas, colas de casos).
- [ ] Skeleton loaders replican la forma real del contenido — no son rectángulos genéricos.

## 13.6 Estados del sistema (doc 11)

- [ ] Los 8 estados están implementados para toda pantalla que consume datos remotos: vacío, con datos, cargando, error, sin conexión, éxito, permisos insuficientes, mantenimiento.
- [ ] El estado "sin conexión" no bloquea silenciosamente — siempre hay un banner/indicador visible.
- [ ] Ningún estado de error es un mensaje genérico ("Algo salió mal") si existe un mensaje específico definido en doc 10.
- [ ] Las pantallas con excepciones documentadas (§11.13: emergencia, cola de casos, matching, cierre de caso, auditoría) implementan su tratamiento especial, no el genérico.

## 13.7 UX Writing / i18n (doc 10, 12)

- [ ] Cero strings hardcodeados — todo texto visible pasa por `t('clave')`.
- [ ] El copy coincide exactamente con el definido en doc 10 (o la desviación fue documentada y justificada).
- [ ] Ningún mensaje de error expone información técnica interna (stack trace, nombre de servicio, código HTTP crudo) al usuario final.
- [ ] Los 3 consentimientos LOPDP están presentes con el texto completo en registro y en `/app/configuracion/privacidad`, no resumidos.

## 13.8 Arquitectura de la información y navegación (doc 02)

- [ ] La ruta implementada coincide exactamente con el sitemap del doc 02 (o la desviación fue documentada).
- [ ] El sidebar muestra únicamente los ítems permitidos para el rol autenticado (tabla §2.5).
- [ ] Breadcrumb presente desde nivel 2, ausente en nivel 0/1, colapsado a "← Volver" en mobile.
- [ ] Acceso sin permiso redirige a `/403`, nunca a `/login` si la sesión es válida.

## 13.9 Flujos (doc 03)

- [ ] El happy path completo fue probado de punta a punta.
- [ ] Cada edge case documentado tiene su tratamiento visible en la UI (no solo manejado silenciosamente en backend).
- [ ] Cada caso de error documentado muestra el mensaje correspondiente (doc 10) y una acción de recuperación.
- [ ] Los estados alternativos (ej. solicitud automática por IoT) fueron probados, no solo el flujo iniciado manualmente.

## 13.10 Rendimiento percibido

- [ ] Ninguna pantalla muestra un spinner de página completa salvo la primera carga del shell (doc 06.29).
- [ ] Los procesos de IA (evaluación de riesgo, matching, generación de guía) muestran mensaje contextual + skeleton, nunca un spinner genérico ni una barra de progreso con porcentaje inventado.
- [ ] Las imágenes/ilustraciones tienen dimensiones reservadas (evita layout shift).
- [ ] React Query configurado con `stale-while-revalidate` — la pantalla muestra el último dato conocido mientras refresca (según arquitectura v4 §5.4).

## 13.11 Casos límite de conectividad (relevante para Paramédico/Paciente móvil)

- [ ] Reconexión con backoff exponencial implementada (1s→2s→4s→8s→30s máx.) y visible al usuario.
- [ ] Formularios críticos (registro de historial en campo, mensajes de chat) conservan el borrador localmente ante pérdida de conexión.
- [ ] La guía de primeros auxilios permanece accesible offline una vez recibida (cacheada).

## 13.12 QA final antes de release de una pantalla

- [ ] Revisión cruzada con el checklist original de `UX.md` (contraste, teclado, semiótica redundante, sin spinners genéricos, áreas táctiles medidas).
- [ ] Captura de pantalla en modo claro y oscuro adjunta al PR.
- [ ] Verificación en al menos 2 breakpoints reales (no solo redimensionar la ventana del navegador — probar en un dispositivo o emulador real).
- [ ] Ningún `console.error`/`console.warn` de accesibilidad en la consola del navegador (React/Radix los reportan si un patrón ARIA está mal usado).
