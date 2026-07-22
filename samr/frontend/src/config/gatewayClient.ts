import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';

/**
 * Cliente HTTP para el API Gateway (Nginx), que expone /api/auth/*, /api/patients/*,
 * /api/solicitud/*, /api/monitoring/*, etc. según ONBOARDING.md sección "Desarrollador Frontend".
 * El BFF (ver apiClient.ts) solo expone /dashboard/ y no debe usarse para el resto de llamadas.
 */
export const gatewayClient = axios.create({
  baseURL: import.meta.env.VITE_GATEWAY_URL || 'https://localhost',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

gatewayClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setAccessToken, logout } = useAuthStore.getState();
  if (!refreshToken) return null;

  try {
    const { data } = await axios.post(
      `${gatewayClient.defaults.baseURL}/api/auth/token/refresh/`,
      { refresh_token: refreshToken }
    );
    setAccessToken(data.access_token);
    return data.access_token as string;
  } catch {
    logout();
    return null;
  }
}

gatewayClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const isAuthEndpoint = originalRequest?.url?.includes('/api/auth/login/') || originalRequest?.url?.includes('/api/auth/token/refresh/');

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;
      refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
      const newToken = await refreshPromise;
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return gatewayClient(originalRequest);
      }
      toast.error('Tu sesión expiró. Inicia sesión de nuevo.');
      return Promise.reject(error);
    }

    if (error.response) {
      const status = error.response.status;
      if (status === 403) {
        toast.error(error.response.data?.error || 'No tienes permiso para esta acción.');
      } else if (status >= 500) {
        toast.error('Error interno del servidor.');
      } else if (!isAuthEndpoint) {
        toast.error(error.response.data?.error || error.response.data?.message || 'Error en la petición.');
      }
    } else if (error.request) {
      toast.error('No se pudo conectar con el API Gateway. Verifique que el backend esté corriendo (https://localhost).');
    }

    return Promise.reject(error);
  }
);
