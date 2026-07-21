# SAMR - Frontend
## Rama `ui/frontend-app`

> Stack React/TypeScript, gestión de estado, resiliencia del cliente y configuración WebRTC. Para el contrato de API que este frontend consume ver `arch/system-design`; para seguridad del lado del cliente (JWT) ver `sec/security-hardening`; para lineamientos visuales/accesibilidad ver `ux/design-prototypes`.

---

# 1. Stack Tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| React | 18.3.1 | Framework UI (componentes funcionales + hooks) |
| TypeScript | 5.5.3 | Tipado estático |
| Vite | 5.3.4 | Build tool y dev server |
| Zustand | 4.5.4 | Estado global por dominio (`authStore`, `solicitudStore`, `monitoringStore`, `evaluacionStore`, `atencionStore`) |
| Axios | 1.7.2 | Cliente HTTP con interceptores JWT |
| React Router DOM | 6.26.0 | Routing SPA con rutas protegidas por rol |
| @tanstack/react-query | 5.51.1 | Cache de datos del servidor, refetch automático |
| Radix UI | (paquetes individuales, última estable) | Componentes accesibles headless (ver `ux/design-prototypes`) |
| Tailwind CSS | 3.4.7 | Sistema de diseño utilitario |
| React Hook Form | 7.52.1 | Formularios con validación |
| Zod | 3.23.8 | Validación de esquemas compartida con el backend |
| Recharts | 2.12.7 | Gráficas de signos vitales |
| react-hot-toast | 2.4.1 | Notificaciones toast |
| Framer Motion | 11.3.8 | Animaciones (estados de urgencia, bot) |
| i18next | 23.12.2 | Internacionalización ES/EN |

---

# 2. Principio Clave: el Frontend solo conoce al BFF

**El Frontend solo conoce la URL del BFF** (`VITE_BFF_URL`) - nunca la del API Gateway (Nginx) directamente, y mucho menos las URLs de los 12 microservicios internos. El BFF es quien conoce la URL del Gateway, y el Gateway quien conoce la topología interna (ver `arch/system-design`, sección de topología). Esto es una capa de indirección intencional: si un microservicio cambia de nombre, puerto o incluso se divide en dos, el Frontend no se entera - solo el BFF y el Gateway necesitan actualizarse.

```
Frontend  →  BFF (VITE_BFF_URL)  →  API Gateway (conocido solo por el BFF)  →  microservicios
```

---

# 3. Gestión de Estado

- **Zustand por dominio** - sin Redux, evita boilerplate innecesario para dominios que no se comunican entre sí:
  - `authStore` - sesión, rol, JWT en memoria (nunca en `localStorage` sin cifrar).
  - `solicitudStore` - estado de la conversación con el bot y la solicitud en curso.
  - `monitoringStore` - últimas lecturas de signos vitales (alimentado por WebSocket).
  - `evaluacionStore` - resultado de evaluación de riesgo y matching en curso.
  - `atencionStore` - estado de la teleconsulta / emergencia activa.
- **Peticiones HTTP:** Axios con interceptor que adjunta el JWT y reintenta una vez tras refrescar el token en un 401. Todas las peticiones van al BFF, no a Nginx.
- **Datos del servidor:** `@tanstack/react-query` con `stale-while-revalidate` - la pantalla muestra el último dato conocido mientras refresca en segundo plano.

---

# 4. Resiliencia del Cliente

- **`ErrorBoundary` por módulo** - un fallo de `solicitud-service` no debe tumbar la pantalla de monitoreo; cada dominio (M1/M2/M3/M4) tiene su propio boundary.
- **`SkeletonLoader`** en toda carga remota - nunca un spinner genérico ni una barra de progreso falsa (ver `ux/design-prototypes` para el razonamiento de por qué).
- **Reconexión WebSocket** con backoff exponencial: 1s → 2s → 4s → 8s → 30s máx.
- **Banner de estado offline** tras 3 intentos fallidos consecutivos.

---

# 5. WebRTC (Teleconsulta)

`RTCPeerConnection` en el cliente, señalización vía el WebSocket ya definido en `logic/core-services` - sin librería adicional de video, WebRTC es nativo del navegador.

```javascript
const pc = new RTCPeerConnection({
  iceServers: [
    { urls: "stun:stun.l.google.com:19302" },
    { urls: "turn:turn.samr.local:3478", username, credential },
  ],
});
// El TURN (coturn) solo se usa cuando la conexión directa P2P falla
// (redes con NAT simétrico o firewalls corporativos).
```

La señal (`offer`/`answer`/`ice-candidate`) viaja por `ws/teleconsult/{room_token}/`; el video/audio viaja peer-to-peer, nunca a través del backend.

---
*Ver también: `arch/system-design` (contrato de endpoints del BFF/Gateway), `sec/security-hardening` (manejo del JWT en el cliente), `ux/design-prototypes` (accesibilidad y jerarquía visual).*
