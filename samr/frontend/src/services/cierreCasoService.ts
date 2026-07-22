import { gatewayClient } from '../config/gatewayClient';

export interface Caso {
  id: string;
  patient_id: string;
  teleconsult_id: string | null;
  emergency_id: string | null;
  clinical_notes: string;
  integrity_hash: string;
  status: 'open' | 'closed';
  closed_at: string | null;
}

export interface CaseReadiness {
  caso_id: string;
  status: string;
  has_clinical_notes: boolean;
  has_attention_source: boolean;
  integrity_valid: boolean;
  ready_to_close: boolean;
}

/** GET /api/cierre-caso/mis-casos/ — patient ve los suyos; el resto ve todos. */
export const getCasos = async (): Promise<Caso[]> => {
  const { data } = await gatewayClient.get<Caso[]>('/api/cierre-caso/mis-casos/');
  return data;
};

/** GET /api/cierre-caso/<id>/verify/ — professional/center_admin/system_admin. */
export const verifyCaso = async (casoId: string): Promise<CaseReadiness> => {
  const { data } = await gatewayClient.get<CaseReadiness>(`/api/cierre-caso/${casoId}/verify/`);
  return data;
};

/** POST /api/cierre-caso/<id>/close/ — exclusivo `professional`. */
export const closeCaso = async (casoId: string, clinicalNotes: string): Promise<Caso> => {
  const { data } = await gatewayClient.post<Caso>(`/api/cierre-caso/${casoId}/close/`, { clinical_notes: clinicalNotes });
  return data;
};
