import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Roles reales del backend (claim JWT `rol`, ver auth-service/apps/auth/models.py)
export type Role = 'patient' | 'professional' | 'nurse' | 'center_admin' | 'system_admin' | 'dpd_delegate';

export interface AuthUser {
  id: string;
  email: string;
  role: Role;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  setAuth: (tokens: AuthTokens, user: AuthUser) => void;
  setAccessToken: (accessToken: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      setAuth: (tokens, user) =>
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          user,
          isAuthenticated: true,
        }),
      setAccessToken: (accessToken) => set({ accessToken }),
      logout: () => set({ accessToken: null, refreshToken: null, user: null, isAuthenticated: false }),
    }),
    { name: 'samr-auth' }
  )
);
