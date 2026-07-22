import { gatewayClient } from '../config/gatewayClient';
import type { AuthUser } from '../store/authStore';

interface TokenPair {
  access_token: string;
  refresh_token: string;
}

/** POST /api/auth/login/ (auth-service, vía Gateway) */
export const login = async (email: string, password: string): Promise<TokenPair> => {
  const { data } = await gatewayClient.post<TokenPair>('/api/auth/login/', { email, password });
  return data;
};

/** GET /api/auth/me/ (auth-service, vía Gateway) */
export const getMe = async (): Promise<AuthUser> => {
  const { data } = await gatewayClient.get<{ id: string; email: string; role: AuthUser['role']; created_at: string }>('/api/auth/me/');
  return { id: data.id, email: data.email, role: data.role };
};

/**
 * POST /api/auth/register/ (auth-service, vía Gateway). El backend crea
 * siempre rol `patient` — no hay autorregistro para personal clínico o
 * administrativo (esos roles se asignan manualmente, fuera de la app).
 */
export const register = async (email: string, password: string): Promise<void> => {
  await gatewayClient.post('/api/auth/register/', { email, password });
};

/** POST /api/auth/password/change/ — requiere sesión activa. */
export const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
  await gatewayClient.post('/api/auth/password/change/', {
    current_password: currentPassword,
    new_password: newPassword,
  });
};

/**
 * POST /api/auth/password/reset/request/ — público. El backend publica el
 * token de recuperación como evento (`auth.password_reset_requested`), que
 * en este MVP solo llega a la bandeja de Notificaciones del usuario (no hay
 * envío de correo real) — por eso solo es recuperable si el usuario puede
 * volver a iniciar sesión, o si soporte se lo entrega manualmente.
 */
export const requestPasswordReset = async (email: string): Promise<void> => {
  await gatewayClient.post('/api/auth/password/reset/request/', { email });
};

/** POST /api/auth/password/reset/confirm/ — público, con el token recibido. */
export const confirmPasswordReset = async (token: string, newPassword: string): Promise<void> => {
  await gatewayClient.post('/api/auth/password/reset/confirm/', { token, new_password: newPassword });
};
