import { gatewayClient } from '../config/gatewayClient';
import type { Alert } from './dashboardService';

/**
 * GET /api/monitoring/alerts/ (monitoring-service, vía Gateway).
 * Exclusivo de professional/nurse/center_admin/system_admin — el rol
 * `patient` recibe 403 (monitoring-service no expone sus propias alertas
 * al paciente, ver apps/monitoring/views.py AlertView.get).
 */
export const getAlerts = async (): Promise<Alert[]> => {
  const { data } = await gatewayClient.get<Alert[]>('/api/monitoring/alerts/');
  return data;
};
