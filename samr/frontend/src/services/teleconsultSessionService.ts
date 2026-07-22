import { gatewayClient } from '../config/gatewayClient';

export interface TeleconsultSession {
  id: string;
  patient_id: string;
  professional_id: string;
  emergency_id: string | null;
  room_token: string;
  status: string;
  created_at: string;
  closed_at: string | null;
}

/**
 * POST /api/teleconsult/ (teleconsult-service, vía Gateway) — exclusivo de
 * professional/center_admin/system_admin. No existe endpoint para listar
 * pacientes disponibles (ver AGENTS.md / gaps de backend), así que el
 * `patient_id` se ingresa manualmente hasta que el backend exponga un listado.
 */
export const createTeleconsultSession = async (patientId: string): Promise<TeleconsultSession> => {
  const { data } = await gatewayClient.post<TeleconsultSession>('/api/teleconsult/', { patient_id: patientId });
  return data;
};
