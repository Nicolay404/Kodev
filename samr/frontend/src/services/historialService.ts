import { gatewayClient } from '../config/gatewayClient';

export interface HistorialEvent {
  event_type: string;
  event_key: string | null;
  [key: string]: unknown;
}

export interface Historial {
  id: string;
  patient_id: string;
  eventos: HistorialEvent[];
  updated_at: string;
}

/**
 * GET /api/historial/<patient_id>/ — el paciente solo puede ver el suyo;
 * professional/nurse/center_admin/system_admin pueden ver el de cualquiera
 * (el backend no valida relación de cuidado todavía).
 */
export const getHistorial = async (patientId: string): Promise<Historial> => {
  const { data } = await gatewayClient.get<Historial>(`/api/historial/${patientId}/`);
  return data;
};

/** POST /api/historial/<patient_id>/ — exclusivo professional/nurse. */
export const addClinicalNote = async (patientId: string, note: string): Promise<Historial> => {
  const { data } = await gatewayClient.post<Historial>(`/api/historial/${patientId}/`, { note });
  return data;
};
