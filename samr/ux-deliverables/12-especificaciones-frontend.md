# 12 - Especificaciones para Frontend
## SAMR - Sistema de Atención Médica Remota

> Traducción directa de los docs 05/06 a artefactos pegables en código. Stack objetivo (según arquitectura v4): React 18.3 + TypeScript 5.5 + Vite + Tailwind CSS 3.4 + Radix UI + Zustand + React Hook Form + Zod + Framer Motion + i18next.

---

## 12.1 Variables CSS (tokens base - `src/styles/tokens.css`)

```css
:root {
  /* Color - primario */
  --color-teal-50: #EFFCFB;
  --color-teal-100: #D7F7F3;
  --color-teal-200: #AEEEE8;
  --color-teal-300: #78DFD6;
  --color-teal-400: #3EC8BC;
  --color-teal-500: #1FA89C;
  --color-teal-600: #148075;
  --color-teal-700: #0F6259;
  --color-teal-800: #0B4A43;
  --color-teal-900: #082F2B;

  /* Color - secundario */
  --color-indigo-500: #6366F1;
  --color-indigo-600: #4F46E5;
  --color-indigo-700: #4338CA;

  /* Color - semántico */
  --color-success-600: #16A34A;
  --color-success-700: #15803D;
  --color-error-600: #DC2626;
  --color-error-700: #B91C1C;
  --color-warning-500: #F59E0B;
  --color-warning-700: #B45309;
  --color-info-600: #2563EB;
  --color-info-700: #1D4ED8;

  /* Color - urgencia clínica (nunca reutilizar fuera de este contexto) */
  --color-urgencia-critico: #B91C1C;
  --color-urgencia-alto: #C2410C;
  --color-urgencia-moderado: #F59E0B;
  --color-urgencia-leve: #15803D;

  /* Color - neutrales */
  --color-gray-50: #F8FAFC;
  --color-gray-100: #F1F5F9;
  --color-gray-200: #E2E8F0;
  --color-gray-300: #CBD5E1;
  --color-gray-400: #94A3B8;
  --color-gray-500: #64748B;
  --color-gray-600: #475569;
  --color-gray-700: #334155;
  --color-gray-800: #1E293B;
  --color-gray-900: #0F172A;

  /* Semántico - modo claro (default) */
  --bg-page: var(--color-gray-50);
  --bg-surface: #FFFFFF;
  --border-default: var(--color-gray-200);
  --text-primary: var(--color-gray-900);
  --text-secondary: var(--color-gray-600);
  --text-disabled: var(--color-gray-400);
  --primary-action: var(--color-teal-600);

  /* Espaciado (base 8px, escala Tailwind-compatible) */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */

  /* Radios */
  --radius-sm: 0.25rem;  /* 4px */
  --radius-md: 0.5rem;   /* 8px */
  --radius-lg: 0.75rem;  /* 12px */
  --radius-xl: 1rem;     /* 16px */
  --radius-full: 9999px;

  /* Sombras */
  --shadow-sm: 0 1px 2px rgba(15,23,42,0.06);
  --shadow-md: 0 4px 6px rgba(15,23,42,0.08);
  --shadow-lg: 0 10px 15px rgba(15,23,42,0.10);
  --shadow-xl: 0 20px 25px rgba(15,23,42,0.12);
  --shadow-2xl: 0 25px 50px rgba(15,23,42,0.18);

  /* Tipografía */
  --font-family-base: 'Inter', system-ui, -apple-system, sans-serif;

  /* Duraciones (doc 08) */
  --duration-instant: 100ms;
  --duration-fast: 150ms;
  --duration-base: 200ms;
  --duration-medium: 300ms;
  --duration-slow: 400ms;

  /* Easing (doc 08) */
  --ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-entrance: cubic-bezier(0, 0, 0.2, 1);
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);
}

:root[data-theme='dark'] {
  --bg-page: var(--color-gray-900);
  --bg-surface: var(--color-gray-800);
  --border-default: var(--color-gray-700);
  --text-primary: var(--color-gray-50);
  --text-secondary: var(--color-gray-400);
  --text-disabled: var(--color-gray-600);
  --primary-action: var(--color-teal-400);
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme='light']) {
    --bg-page: var(--color-gray-900);
    --bg-surface: var(--color-gray-800);
    --border-default: var(--color-gray-700);
    --text-primary: var(--color-gray-50);
    --text-secondary: var(--color-gray-400);
    --text-disabled: var(--color-gray-600);
    --primary-action: var(--color-teal-400);
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 12.2 Extensión de Tailwind config (`tailwind.config.ts`)

```ts
import type { Config } from 'tailwindcss'

export default {
  darkMode: ['class', '[data-theme="dark"]'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        teal: {
          50: '#EFFCFB', 100: '#D7F7F3', 200: '#AEEEE8', 300: '#78DFD6',
          400: '#3EC8BC', 500: '#1FA89C', 600: '#148075', 700: '#0F6259',
          800: '#0B4A43', 900: '#082F2B',
        },
        urgencia: {
          critico: '#B91C1C',
          alto: '#C2410C',
          moderado: '#F59E0B',
          leve: '#15803D',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        critico: ['1.125rem', { lineHeight: '1.75rem', fontWeight: '600' }], // 18px mínimo (doc 05/09)
      },
      spacing: {
        // Alineado 1:1 con la escala Tailwind por defecto - sin overrides necesarios
      },
      borderRadius: {
        sm: '0.25rem', md: '0.5rem', lg: '0.75rem', xl: '1rem',
      },
      boxShadow: {
        sm: '0 1px 2px rgba(15,23,42,0.06)',
        md: '0 4px 6px rgba(15,23,42,0.08)',
        lg: '0 10px 15px rgba(15,23,42,0.10)',
        xl: '0 20px 25px rgba(15,23,42,0.12)',
        '2xl': '0 25px 50px rgba(15,23,42,0.18)',
      },
      transitionDuration: {
        instant: '100ms', fast: '150ms', base: '200ms', medium: '300ms', slow: '400ms',
      },
      animation: {
        'pulse-critico': 'pulse-critico 1s cubic-bezier(0.4,0,0.2,1) infinite', // 1Hz, doc 08 §8.6
        shimmer: 'shimmer 1.5s linear infinite',
      },
      keyframes: {
        'pulse-critico': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.85' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      screens: {
        // Coincide con doc 07 §7.1 - valores por defecto de Tailwind, documentado explícitamente
        sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1536px',
      },
    },
  },
  plugins: [],
} satisfies Config
```

**Regla de uso**: nunca escribir un color hexadecimal literal (`#148075`) dentro de un componente - siempre vía clase Tailwind (`bg-teal-600`) o variable CSS (`var(--primary-action)`) cuando el valor debe responder a modo claro/oscuro dinámicamente.

## 12.3 Clases Tailwind - patrones de referencia por componente

```
Botón primario md:      bg-teal-600 hover:bg-teal-700 active:scale-[0.98] text-white
                         h-10 px-4 rounded-md font-medium transition-colors duration-instant
                         focus-visible:ring-2 focus-visible:ring-teal-600 focus-visible:ring-offset-2
                         disabled:opacity-40 disabled:cursor-not-allowed

Input default:           h-10 px-3 rounded-md border border-gray-300 bg-white
                         focus:border-teal-600 focus:ring-2 focus:ring-teal-600
                         aria-invalid:border-error-600

Card interactiva:        bg-white rounded-lg shadow-sm hover:shadow-md hover:-translate-y-0.5
                         transition-all duration-base p-4 cursor-pointer

Card urgencia (crítico): border-l-4 border-urgencia-critico animate-pulse-critico

Badge urgencia crítico:  bg-urgencia-critico text-white text-xs font-semibold px-2 py-1 rounded-sm
                         flex items-center gap-1  /* ícono + texto, nunca solo color */

Skeleton:                bg-gray-200 dark:bg-gray-700 rounded-md
                         bg-[length:200%_100%] bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200
                         animate-shimmer
```

## 12.4 Naming convention

| Ámbito | Convención | Ejemplo |
|---|---|---|
| Componentes React | `PascalCase`, un componente por archivo | `CasoCard.tsx`, `EmergenciaGuia.tsx` |
| Hooks | `camelCase` con prefijo `use` | `useMatchingCentros.ts`, `useReconexion.ts` |
| Stores Zustand | `camelCase` con sufijo `Store` | `authStore.ts`, `solicitudStore.ts`, `evaluacionStore.ts`, `monitoringStore.ts`, `atencionStore.ts` |
| Tipos/interfaces | `PascalCase`, sin prefijo `I` | `SolicitudMedica`, `NivelRiesgo` |
| Tokens de diseño (CSS vars) | `kebab-case` con prefijo semántico | `--color-teal-600`, `--space-4` |
| Rutas (React Router) | `kebab-case`, coincide con el sitemap (doc 02) | `/app/casos/:id/matching` |
| Claves de i18n | `snake_case` jerárquico por módulo | `solicitud.chat.placeholder`, `errores.red_generica` |
| Archivos de test | mismo nombre + `.test.tsx` | `CasoCard.test.tsx` |

## 12.5 Estructura de carpetas (`ui/frontend-app`)

Alineada con la organización por dominio de Zustand ya definida en la arquitectura v4 (`authStore`, `solicitudStore`, `monitoringStore`, `evaluacionStore`, `atencionStore`) y con los módulos M1–M4:

```
src/
├── app/
│   ├── routes/                    # definición de rutas (React Router), 1:1 con doc 02
│   ├── AppShell.tsx                # Navbar + Sidebar + Outlet
│   └── ProtectedRoute.tsx          # guard de RBAC → /403 si no hay permiso
│
├── design-system/                  # doc 06 - componentes puros, sin lógica de negocio
│   ├── Button/
│   ├── Input/
│   ├── Card/
│   ├── Badge/
│   ├── UrgenciaBadge/               # componente específico de dominio (color+ícono+texto)
│   ├── Modal/
│   ├── Toast/
│   ├── Skeleton/
│   └── ... (uno por componente del doc 06)
│
├── features/                       # organizado por módulo de negocio (M1–M4)
│   ├── auth/                       # login, registro, recuperar contraseña
│   │   ├── components/
│   │   ├── hooks/
│   │   └── authStore.ts
│   ├── solicitud/                  # M1
│   │   ├── components/             # ChatSolicitud, SolicitudDetalle, StepperEstado
│   │   ├── hooks/
│   │   └── solicitudStore.ts
│   ├── monitoring/                 # M1 - dispositivos IoT (vista paciente)
│   │   └── monitoringStore.ts
│   ├── evaluacion/                 # M2
│   │   ├── components/             # ColaCasos, DetalleCaso, Matching
│   │   └── evaluacionStore.ts
│   ├── atencion/                   # M3
│   │   ├── components/             # SalaTeleconsulta, EmergenciaActiva, CierreCaso
│   │   └── atencionStore.ts
│   ├── historial/                  # M4 - expediente clínico
│   ├── admin/                      # M4 - centros y dispositivos
│   └── auditoria/                  # M4 - DPD
│
├── shared/
│   ├── i18n/
│   │   ├── es.json                 # fuente - deriva de doc 10
│   │   └── en.json
│   ├── lib/                        # axios interceptors, react-query client
│   ├── hooks/                      # useReconexion, usePermisos, useReducedMotion
│   └── utils/
│
├── styles/
│   └── tokens.css                  # doc 12 §12.1
│
└── types/
    └── dominio.ts                  # tipos compartidos derivados del modelo de dominio (Apéndice A, samr_documentacion)
```

**Regla de dependencia**: `design-system/` nunca importa de `features/` (los componentes base no conocen el dominio clínico); `features/` sí importa de `design-system/`. Esto mantiene el Design System reutilizable y testeable en aislamiento.

## 12.6 Convenciones de diseño (checklist de coherencia)

1. Ningún componente nuevo se crea en `features/` si ya existe un equivalente genérico en `design-system/` - se extiende vía props, no se duplica.
2. Todo texto visible al usuario pasa por `t('clave.i18n')` (i18next) - cero strings hardcodeados en JSX, incluso si hoy el sistema solo se usa en español (doc 10 es la fuente de `es.json`).
3. Todo color de urgencia se consume exclusivamente a través del componente `UrgenciaBadge` (que ya encapsula color+ícono+texto+pulso) - nunca se aplica `bg-urgencia-critico` suelto en un componente ad hoc, para no romper accidentalmente la semiótica redundante (doc 05/09).
4. Todo componente que muestra datos remotos implementa sus 8 estados (doc 11) mediante los mismos componentes base (`Skeleton`, `EmptyState`, `ErrorState`) - no se improvisa un `if (loading) return <p>Cargando...</p>` local.

## 12.7 Contrato real con el backend - detalles de integración (nuevo, v1.1)

> Ver [00 - Alineación con el Backend Real](00-alineacion-backend.md) para el detalle completo. Esta sección resume lo que específicamente afecta código de integración (clientes HTTP, interceptores, stores), no decisiones de diseño visual.

- **El claim de rol en el JWT se llama `rol`, no `role`.** Todo el backend (`request.user.rol`) y el propio token (`{usuario_id, email, rol, type, iat, jti, iss}`) usan esa clave literal. El hook `usePermisos`/`authStore` debe leer `decodedToken.rol` - un typo aquí (`role`) falla silenciosamente en TypeScript si el tipo no está bien definido.
- **El BFF (`bff-service`, puerto 8000, fuera de Nginx) es de solo lectura.** Expone únicamente `GET /health` y `GET /dashboard/` (CORS configurado con `allow_methods=["GET"]` exclusivamente). **Ninguna mutación pasa por el BFF** - todo `POST`/`PATCH`/`DELETE` va directo al API Gateway (Nginx, rutas `/api/<servicio>/...`) con el JWT del usuario, igual que describe la arquitectura v4. El cliente Axios necesita dos `baseURL` configurados: uno para el BFF (solo dashboard) y otro para el gateway (todo lo demás).
- **`/dashboard/` del BFF devuelve siempre las mismas 4 claves** (`patient`, `evaluacion`, `monitoring`, `atencion`), sin diferenciar por rol (doc 00 §G8). Para roles distintos de `patient`, el store de dashboard debe ignorar el BFF y componer sus datos con llamadas directas al gateway (ver doc 04 §4.3, columna "Fuente de datos").
- **Token de servicio (`X-Service-Token`) nunca se usa desde el frontend** - es exclusivo de llamadas máquina-a-máquina entre microservicios (ej. `GET /api/evaluacion/centros-disponibles/`, `GET /api/patients/{id}/summary/`). Si una pantalla de frontend parece necesitar un endpoint que solo acepta `X-Service-Token`, es una señal de que ese endpoint no está pensado para consumo directo del cliente - hay que resolverlo por otra vía o escalarlo como brecha (doc 14), nunca embebiendo el token de servicio en el bundle del frontend (fuga de credencial).
- **Vida del token**: `access_token` expira en 15 minutos, `refresh_token` en 7 días. El interceptor de Axios debe reintentar una vez tras refrescar en un 401 (ya especificado en doc 04 §5.4 de la arquitectura), pero como no existe endpoint de "cerrar sesión" del lado del servidor (doc 00 §G14), cerrar sesión es puramente client-side: descartar ambos tokens del storage.
- **Endpoints que devuelven listas sin paginación real** (`GET /mis-casos/`, `GET /decisions/`, `GET /api/emergencies/`): todos capados a un número fijo (50 o 100) sin `?page=`/`?cursor=`. No implementar UI de paginación contra estos endpoints - cualquier "paginación" posible es solo scroll/filtro sobre el array ya recibido.
