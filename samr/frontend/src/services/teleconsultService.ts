import { gatewayClient } from '../config/gatewayClient';

export interface CreateSolicitudDto {
  sintomas: string[];
  fuente?: 'chatbot' | 'iot_anomalia' | 'manual';
}

export interface Solicitud {
  id: string;
  patient_id: string;
  sintomas: string[];
  datos_biomedicos: Record<string, unknown>;
  fuente: 'chatbot' | 'iot_anomalia' | 'manual';
  estado: 'pendiente' | 'validada' | 'rechazada' | 'pendiente_reintento';
  created_at: string;
}

/**
 * POST /api/solicitud/ (solicitud-service, vía Gateway) — exclusivo del rol `patient`.
 */
export const createSolicitud = async (data: CreateSolicitudDto): Promise<Solicitud> => {
  const { data: response } = await gatewayClient.post<Solicitud>('/api/solicitud/', data);
  return response;
};
