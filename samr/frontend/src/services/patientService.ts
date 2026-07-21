import { apiClient } from '../config/apiClient';

export interface Patient {
  id: string;
  name: string;
  cedula: string;
  age: number;
  bloodType: string;
  riskLevel: 'Bajo' | 'Medio' | 'Alto';
  lastVisit: string;
}

/**
 * Llama al endpoint de pacientes proxyado por el BFF
 */
export const getPatients = async (): Promise<Patient[]> => {
  // Según scratch_arch.md, la ruta de pacientes es /api/patients/me/
  const { data } = await apiClient.get<Patient[]>('/api/patients/me/');
  return data;
};

export const getPatientSummary = async (patientId: string): Promise<any> => {
  const { data } = await apiClient.get(`/api/patients/${patientId}/summary/`);
  return data;
};
