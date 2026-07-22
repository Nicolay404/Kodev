import { Bell, Check } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useNotifications, useMarkNotificationRead } from '../../hooks/useNotifications';
import type { Notification } from '../../services/notificationService';

/**
 * event_type es la routing key del evento de dominio que la disparó
 * (ej. "emergency.dispatched", "teleconsult.session_started"). No hay un
 * campo de texto legible en el backend — se arma un resumen a partir de
 * las llaves reconocibles del payload.
 */
function summarize(notification: Notification): string {
  const label = notification.event_type.replace(/[._]/g, ' ');
  const payload = notification.payload || {};
  const parts = Object.entries(payload)
    .filter(([key]) => key !== 'usuario_id')
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${String(value).slice(0, 8)}`);
  return parts.length ? `${label} — ${parts.join(', ')}` : label;
}

export function NotificationsList() {
  const { data: notifications, isLoading } = useNotifications();
  const { mutate: markRead } = useMarkNotificationRead();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Notificaciones</h1>
        <p className="text-gray-600 text-sm">
          Bandeja interna (notification-service). No hay envío push real todavía — MVP_NOTIFICATION_BACKEND=log.
        </p>
      </div>

      <div className="bg-surface rounded-lg shadow-sm border border-gray-200 divide-y divide-gray-100">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="p-4"><Skeleton className="h-4 w-3/4" /></div>
          ))
        ) : !notifications || notifications.length === 0 ? (
          <div className="p-8 text-center text-gray-500 flex flex-col items-center gap-2">
            <Bell className="w-8 h-8 text-gray-300" />
            No tienes notificaciones.
          </div>
        ) : (
          notifications.map((n) => (
            <div key={n.id} className={`p-4 flex items-start justify-between gap-4 ${!n.read ? 'bg-teal-50/40' : ''}`}>
              <div className="flex items-start gap-3">
                <span className={`w-2 h-2 mt-2 rounded-full shrink-0 ${!n.read ? 'bg-teal-500' : 'bg-gray-300'}`} />
                <div>
                  <p className="text-sm text-gray-900">{summarize(n)}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{new Date(n.created_at).toLocaleString()}</p>
                </div>
              </div>
              {!n.read && (
                <Button variant="ghost" size="sm" onClick={() => markRead(n.id)} title="Marcar como leída">
                  <Check className="w-4 h-4" />
                </Button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
