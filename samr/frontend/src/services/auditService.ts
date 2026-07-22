import { gatewayClient } from '../config/gatewayClient';

export interface AuditReview {
  id: string;
  audit_log_id: number;
  estado_revision: 'pendiente' | 'revisado' | 'observado';
  revisado_por: string | null;
  comentario: string | null;
  fecha_revision: string | null;
  created_at: string;
}

export interface AuditLog {
  id: number;
  event_type: string;
  actor_id: string | null;
  payload: Record<string, unknown>;
  ai_confidence: string | null;
  ai_explainability: Record<string, unknown> | null;
  created_at: string;
  review: AuditReview | null;
  reviews: AuditReview[];
}

export interface AuditFilters {
  event_type?: string;
  actor_id?: string;
  created_from?: string;
  created_to?: string;
  limit?: number;
  offset?: number;
}

/** GET /api/audit/decisions/ — exclusivo dpd_delegate. Filtros y paginación server-side reales. */
export const getAuditDecisions = async (filters: AuditFilters): Promise<AuditLog[]> => {
  const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== undefined && v !== ''));
  const { data } = await gatewayClient.get<AuditLog[]>('/api/audit/decisions/', { params });
  return data;
};

/** PATCH /api/audit/decisions/<id>/review/ */
export const reviewAuditDecision = async (
  auditLogId: number,
  estadoRevision: 'revisado' | 'observado',
  comentario?: string
): Promise<AuditReview> => {
  const { data } = await gatewayClient.patch<AuditReview>(`/api/audit/decisions/${auditLogId}/review/`, {
    estado_revision: estadoRevision,
    comentario,
  });
  return data;
};
