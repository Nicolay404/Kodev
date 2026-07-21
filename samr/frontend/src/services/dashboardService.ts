import { apiClient } from '../config/apiClient';

export interface DashboardStats {
  active: number;
  pending: number;
  resolved: number;
  totalPatients: number;
}

export interface TeleconsultRequest {
  id: string;
  patient: string;
  cedula: string;
  time: string;
  reason: string;
  status: 'En Espera' | 'En Consulta' | 'Resuelto';
  priority: 'Alta' | 'Media' | 'Baja';
}

export interface DashboardResponse {
  stats: DashboardStats;
  recentRequests: TeleconsultRequest[];
}

/**
 * Llama al endpoint exclusivo del BFF que agrega toda la data necesaria para el Dashboard
 */
export const getDashboardData = async (): Promise<DashboardResponse> => {
  const { data } = await apiClient.get<DashboardResponse>('/dashboard/');
  return data;
};
