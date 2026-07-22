import { gatewayClient } from '../config/gatewayClient';

export interface Notification {
  id: string;
  event_type: string;
  payload: Record<string, unknown>;
  read: boolean;
  created_at: string;
}

/** GET /api/notifications/ (notification-service, vía Gateway). MVP_NOTIFICATION_BACKEND=log: solo bandeja interna, sin push real. */
export const getNotifications = async (): Promise<Notification[]> => {
  const { data } = await gatewayClient.get<Notification[]>('/api/notifications/');
  return data;
};

/** PATCH /api/notifications/<id>/read/ */
export const markNotificationRead = async (id: string): Promise<Notification> => {
  const { data } = await gatewayClient.patch<Notification>(`/api/notifications/${id}/read/`);
  return data;
};
