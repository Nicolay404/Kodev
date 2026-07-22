import { gatewayClient } from '../config/gatewayClient';

export interface FirstAidGuide {
  id: string;
  contenido: string;
  fecha_generacion: string;
}

export interface Emergency {
  id: string;
  patient_id: string;
  triage_level: string;
  status: 'pending' | 'dispatched' | 'closed';
  created_at: string;
  guides: FirstAidGuide[];
}

/** GET /api/emergencies/ — patient ve las suyas; profesional/nurse/center_admin/system_admin ven todas. */
export const getEmergencies = async (): Promise<Emergency[]> => {
  const { data } = await gatewayClient.get<Emergency[]>('/api/emergencies/');
  return data;
};

/** GET /api/emergencies/<id>/ */
export const getEmergency = async (id: string): Promise<Emergency> => {
  const { data } = await gatewayClient.get<Emergency>(`/api/emergencies/${id}/`);
  return data;
};

/** POST /api/emergencies/ — exclusivo de `patient`. */
export const reportEmergency = async (triageLevel: string): Promise<Emergency> => {
  const { data } = await gatewayClient.post<Emergency>('/api/emergencies/', { triage_level: triageLevel });
  return data;
};

/** POST /api/emergencies/<id>/dispatch/ — exclusivo de professional/nurse/center_admin/system_admin. */
export const dispatchEmergency = async (id: string): Promise<Emergency> => {
  const { data } = await gatewayClient.post<Emergency>(`/api/emergencies/${id}/dispatch/`);
  return data;
};
