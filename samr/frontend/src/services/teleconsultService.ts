import { apiClient } from '../config/apiClient';
import type { TeleconsultRequest } from './dashboardService';

export interface CreateRequestDto {
  patientId: string;
  reason: string;
  priority: string;
}

/**
 * Llama al endpoint de solicitud proxyado por el BFF
 */
export const createTeleconsultRequest = async (requestData: CreateRequestDto): Promise<TeleconsultRequest> => {
  // Según scratch_arch.md, la creación de solicitud es POST /api/solicitud/
  const { data } = await apiClient.post<TeleconsultRequest>('/api/solicitud/', requestData);
  return data;
};
