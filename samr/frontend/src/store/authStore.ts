import { create } from 'zustand';

interface User {
  id: string;
  name: string;
  role: 'medical_staff' | 'system_admin' | 'dpd_delegate' | 'patient';
}

interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  setAuth: (token, user) => set({ token, user }),
  logout: () => set({ token: null, user: null }),
}));
