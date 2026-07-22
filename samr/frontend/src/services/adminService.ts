import { gatewayClient } from '../config/gatewayClient';

export interface Center {
  id: string;
  name: string;
  type: string;
  latitude: string | null;
  longitude: string | null;
  status: 'pending_validation' | 'validated' | 'rejected';
}

export interface RegisterCenterDto {
  name: string;
  type: string;
  latitude?: number;
  longitude?: number;
  license_number: string;
  specialties: string[];
}

export interface Device {
  id: string;
  patient_id: string;
  device_type: string;
  registered_by: string;
  active: boolean;
}

export interface RegisterDeviceDto {
  patient_id: string;
  device_type: string;
  serial_number: string;
}

export interface FAQ {
  id: string;
  question: string;
  answer: string;
  updated_at: string;
}

// --- Centros (admin-integracion-service, exclusivo system_admin) ---

export const getCenters = async (status?: string): Promise<Center[]> => {
  const { data } = await gatewayClient.get<Center[]>('/api/admin/centers/', { params: status ? { status } : undefined });
  return data;
};

export const registerCenter = async (dto: RegisterCenterDto): Promise<Center> => {
  const { data } = await gatewayClient.post<Center>('/api/admin/centers/register/', dto);
  return data;
};

// --- Dispositivos ---

export const getDevices = async (): Promise<Device[]> => {
  const { data } = await gatewayClient.get<Device[]>('/api/admin/devices/');
  return data;
};

export const registerDevice = async (dto: RegisterDeviceDto): Promise<Device> => {
  const { data } = await gatewayClient.post<Device>('/api/admin/devices/register/', dto);
  return data;
};

// --- FAQ del chatbot (solicitud-service) ---

export const getFAQs = async (): Promise<FAQ[]> => {
  const { data } = await gatewayClient.get<FAQ[]>('/api/solicitud/faq/');
  return data;
};

export const createFAQ = async (question: string, answer: string): Promise<FAQ> => {
  const { data } = await gatewayClient.post<FAQ>('/api/solicitud/faq/', { question, answer });
  return data;
};

export const updateFAQ = async (id: string, question: string, answer: string): Promise<FAQ> => {
  const { data } = await gatewayClient.patch<FAQ>('/api/solicitud/faq/', { id, question, answer });
  return data;
};
