import { gatewayClient } from '../config/gatewayClient';

export interface PatientProfile {
  id: string;
  user_id: string;
  blood_type: string;
  allergies: string[];
  chronic_conditions: string[];
  latitude: string | null;
  longitude: string | null;
  consent_data: boolean;
  consent_ai: boolean;
  consent_sharing: boolean;
}

export interface PatientProfileDto {
  cedula?: string;
  blood_type?: string;
  allergies?: string[];
  chronic_conditions?: string[];
  consent_data?: boolean;
  consent_ai?: boolean;
  consent_sharing?: boolean;
}

/** GET /api/patients/me/ — exclusivo `patient`. 404 si aún no completó su perfil. */
export const getMyProfile = async (): Promise<PatientProfile> => {
  const { data } = await gatewayClient.get<PatientProfile>('/api/patients/me/');
  return data;
};

/** PATCH /api/patients/me/ — crea el perfil (requiere `cedula`) si no existe, o lo actualiza. */
export const updateMyProfile = async (dto: PatientProfileDto): Promise<PatientProfile> => {
  const { data } = await gatewayClient.patch<PatientProfile>('/api/patients/me/', dto);
  return data;
};
