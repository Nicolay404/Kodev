import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const bffUrl = import.meta.env.VITE_BFF_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: bffUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    // Inject JWT token from Zustand store
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 refresh token logic here as per architecture specs
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Call BFF refresh token endpoint
        // If it succeeds, update useAuthStore token and retry request
        // If it fails, clear auth store and redirect to login
      } catch (refreshError) {
        useAuthStore.getState().logout();
      }
    }
    return Promise.reject(error);
  }
);
