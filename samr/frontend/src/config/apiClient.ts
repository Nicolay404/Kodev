import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';

/**
 * Cliente HTTP configurado para comunicarse EXCLUSIVAMENTE con el BFF-SERVICE,
 * que solo expone /health y /dashboard/ (ver bff/bff-service/main.py). Cualquier
 * otra llamada (auth, patients, solicitud, etc.) debe usar gatewayClient.ts.
 */
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BFF_URL || 'http://localhost:8000',
  timeout: 15000, // 15 segundos de timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de Peticiones: Inyectar JWT Token (RS256) desde el store unificado
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de Respuestas: Manejo global de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Errores HTTP devueltos por el BFF o el Gateway
      const status = error.response.status;

      if (status === 401) {
        toast.error('Sesión expirada o token inválido. Por favor, inicie sesión.');
        // El BFF no soporta refresh; se exige un login nuevo.
        useAuthStore.getState().logout();
      } else if (status >= 500) {
        toast.error('Error interno del servidor BFF o microservicios.');
      } else {
        // Mostrar mensaje de error de negocio si el BFF lo envía
        toast.error(error.response.data?.message || 'Error en la petición.');
      }
    } else if (error.request) {
      // El BFF no responde (servidor caído, CORS o sin internet)
      toast.error('No se pudo conectar con el servidor BFF (localhost:8000). Verifique que esté corriendo.');
    } else {
      toast.error('Error inesperado al preparar la petición.');
    }
    
    return Promise.reject(error);
  }
);
