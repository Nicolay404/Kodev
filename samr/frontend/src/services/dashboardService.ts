import { apiClient } from '../config/apiClient';
import type { Role } from '../store/authStore';

/**
 * Forma real de la respuesta del BFF: GET /dashboard/ resuelve el rol desde el
 * JWT y agrega en paralelo un set de llamadas distinto por rol (ver
 * bff/bff-service/main.py, endpoints_by_role). Cada clave puede faltar según
 * el rol, y si el servicio de origen falla, llega como { error }.
 */
export interface BackendError {
  error: number | string;
}

export interface PatientProfile {
  id: string;
  blood_type: string;
  allergies: string[];
  chronic_conditions: string[];
  consent_data: boolean;
  consent_ai: boolean;
  consent_sharing: boolean;
}

export interface Solicitud {
  id: string;
  patient_id: string;
  sintomas: string[];
  fuente: 'chatbot' | 'iot_anomalia' | 'manual';
  estado: 'pendiente' | 'validada' | 'rechazada' | 'pendiente_reintento';
  created_at: string;
}

export interface Evaluacion {
  id: string;
  solicitud_id: string;
  nivel_riesgo: 'critico' | 'alto' | 'medio' | 'bajo';
  created_at: string;
}

export interface Alert {
  id: string;
  patient_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  created_at: string;
}

export interface Caso {
  id: string;
  patient_id: string;
  teleconsult_id: string | null;
  emergency_id: string | null;
  status: 'open' | 'closed';
  closed_at: string | null;
}

export interface Emergencia {
  id: string;
  patient_id: string;
  triage_level: string;
  created_at: string;
}

export interface TeleconsultaSesion {
  id: string;
  patient_id: string;
  professional_id: string;
  room_token: string;
  status: string;
  created_at: string;
}

export interface Notificacion {
  id: string;
  title?: string;
  message?: string;
  read?: boolean;
  created_at?: string;
}

/**
 * Cada clave es opcional: el BFF solo la incluye si el rol del usuario la tiene
 * asignada en endpoints_by_role. Cuando está presente, puede venir como error.
 */
export interface DashboardResponse {
  role: Role;
  patient?: PatientProfile | BackendError;
  solicitudes?: Solicitud[] | BackendError;
  evaluacion?: Evaluacion[] | BackendError;
  monitoring?: Alert[] | BackendError;
  atencion?: Caso[] | BackendError;
  emergencias?: Emergencia[] | BackendError;
  teleconsultas?: TeleconsultaSesion[] | BackendError;
  notificaciones?: Notificacion[] | BackendError;
  centros?: unknown | BackendError;
  dispositivos?: unknown | BackendError;
  faq?: unknown | BackendError;
  auditoria?: unknown | BackendError;
}

export function isBackendError<T>(value: T | BackendError | undefined): value is BackendError {
  return typeof value === 'object' && value !== null && 'error' in value;
}

/** Devuelve el arreglo si la clave está presente y no vino con error; si no, []. */
export function asList<T>(value: T[] | BackendError | undefined): T[] {
  if (!value || isBackendError(value)) return [];
  return value;
}

/**
 * Llama al endpoint exclusivo del BFF que agrega toda la data necesaria para el Dashboard
 */
export const getDashboardData = async (): Promise<DashboardResponse> => {
  const { data } = await apiClient.get<DashboardResponse>('/dashboard/');
  return data;
};
