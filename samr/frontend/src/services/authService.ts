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
