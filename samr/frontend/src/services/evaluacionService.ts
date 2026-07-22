import { gatewayClient } from '../config/gatewayClient';

export interface Matching {
  id: string;
  evaluacion: string;
  professional_id: string;
  center_id: string;
  score: string;
}

export interface MatchingDto {
  patient_id: string;
  professional_id?: string;
  center_id?: string;
}

/**
 * POST /api/evaluacion/matching/<evaluacion_id>/ — professional/center_admin.
 * No hay endpoint accesible desde el navegador para listar centros disponibles
 * (CentrosDisponiblesView usa token de servicio, no JWT de usuario) — si no se
 * envía `center_id`, el backend auto-asigna el mejor centro disponible.
 */
export const createMatching = async (evaluacionId: string, dto: MatchingDto): Promise<Matching> => {
  const { data } = await gatewayClient.post<Matching>(`/api/evaluacion/matching/${evaluacionId}/`, dto);
  return data;
};
