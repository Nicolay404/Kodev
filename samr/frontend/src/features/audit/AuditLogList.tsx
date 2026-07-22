import { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X, ShieldCheck } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAuditDecisions, useReviewAuditDecision } from '../../hooks/useAudit';
import type { AuditLog } from '../../services/auditService';

const PAGE_SIZE = 20;

const REVIEW_LABEL: Record<string, string> = {
  pendiente: 'Pendiente',
  revisado: 'Revisado',
  observado: 'Observado',
};

const REVIEW_STYLE: Record<string, string> = {
  pendiente: 'bg-gray-100 text-gray-600 border-gray-200',
  revisado: 'bg-success-50 text-success-700 border-success-200',
  observado: 'bg-warning-50 text-warning-700 border-warning-200',
};

export function AuditLogList() {
  const [eventType, setEventType] = useState('');
  const [actorId, setActorId] = useState('');
  const [page, setPage] = useState(0);
  const [selected, setSelected] = useState<AuditLog | null>(null);
  const [comentario, setComentario] = useState('');

  const { data: logs, isLoading } = useAuditDecisions({
    event_type: eventType || undefined,
    actor_id: actorId || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  });
  const { mutate: review, isPending: reviewing } = useReviewAuditDecision();

  const handleReview = (estado: 'revisado' | 'observado') => {
    if (!selected) return;
    review(
      { id: selected.id, estado, comentario: comentario || undefined },
      { onSuccess: () => { setSelected(null); setComentario(''); } }
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Auditoría de Decisiones</h1>
        <p className="text-gray-600 text-sm">Registro append-only de eventos del sistema (audit-service), exclusivo del Delegado de Protección de Datos.</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          value={eventType}
          onChange={(e) => { setEventType(e.target.value); setPage(0); }}
          placeholder="Filtrar por event_type (ej. emergency.created)"
          className="px-3 py-2 border border-gray-300 rounded-md text-sm flex-1 min-w-50"
        />
        <input
          value={actorId}
          onChange={(e) => { setActorId(e.target.value); setPage(0); }}
          placeholder="Filtrar por actor_id (UUID)"
          className="px-3 py-2 border border-gray-300 rounded-md text-sm flex-1 min-w-50"
        />
      </div>

      <div className="bg-surface rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Evento</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Fecha</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Revisión</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i}><td className="px-6 py-4" colSpan={5}><Skeleton className="h-4 w-full" /></td></tr>
                ))
              ) : !logs || logs.length === 0 ? (
                <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No hay registros para estos filtros.</td></tr>
              ) : (
                logs.map((log) => {
                  const state = log.review?.estado_revision ?? 'pendiente';
                  return (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-500">#{log.id}</td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{log.event_type}</td>
                      <td className="px-6 py-4 text-sm text-gray-500 hidden sm:table-cell">{new Date(log.created_at).toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${REVIEW_STYLE[state]}`}>
                          {REVIEW_LABEL[state]}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Button variant="outline" size="sm" onClick={() => setSelected(log)}>Ver</Button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-gray-200 flex justify-between items-center text-sm text-gray-500">
          <span>Página {page + 1}</span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage((p) => Math.max(0, p - 1))}>Anterior</Button>
            <Button variant="outline" size="sm" disabled={!logs || logs.length < PAGE_SIZE} onClick={() => setPage((p) => p + 1)}>Siguiente</Button>
          </div>
        </div>
      </div>

      <Dialog.Root open={!!selected} onOpenChange={(open) => !open && setSelected(null)}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] bg-surface rounded-lg shadow-lg p-6 animate-in fade-in zoom-in duration-200 max-h-[85vh] overflow-y-auto">
            {selected && (
              <>
                <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-4">
                  <Dialog.Title className="text-lg font-bold text-gray-900">Registro #{selected.id}</Dialog.Title>
                  <Dialog.Close asChild>
                    <button className="text-gray-400 hover:text-gray-600 p-1" aria-label="Cerrar"><X className="w-5 h-5" /></button>
                  </Dialog.Close>
                </div>
                <div className="space-y-4 text-sm">
                  <div>
                    <span className="text-gray-500 block text-xs">Evento</span>
                    <span className="font-medium">{selected.event_type}</span>
                  </div>
                  {selected.actor_id && (
                    <div>
                      <span className="text-gray-500 block text-xs">Actor</span>
                      <span className="font-medium">{selected.actor_id}</span>
                    </div>
                  )}
                  {selected.ai_confidence !== null && (
                    <div>
                      <span className="text-gray-500 block text-xs">Confianza IA</span>
                      <span className="font-medium">{selected.ai_confidence}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-500 block text-xs mb-1">Payload</span>
                    <pre className="bg-gray-50 border border-gray-100 rounded-md p-3 text-xs overflow-x-auto">
                      {JSON.stringify(selected.payload, null, 2)}
                    </pre>
                  </div>

                  {selected.reviews.length > 0 && (
                    <div>
                      <span className="text-gray-500 block text-xs mb-1">Historial de revisiones</span>
                      <div className="space-y-2">
                        {selected.reviews.map((r) => (
                          <div key={r.id} className="border border-gray-100 rounded-md p-2 text-xs">
                            <span className={`px-2 py-0.5 rounded-full border ${REVIEW_STYLE[r.estado_revision]}`}>{REVIEW_LABEL[r.estado_revision]}</span>
                            {r.comentario && <p className="mt-1 text-gray-600">{r.comentario}</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-4 border-t border-gray-100 space-y-2">
                    <label className="block text-xs font-medium text-gray-700">Comentario (opcional)</label>
                    <textarea
                      value={comentario}
                      onChange={(e) => setComentario(e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                    <div className="flex gap-2">
                      <Button className="flex-1" disabled={reviewing} onClick={() => handleReview('revisado')}>
                        <ShieldCheck className="w-4 h-4 mr-1" /> Marcar Revisado
                      </Button>
                      <Button variant="outline" className="flex-1" disabled={reviewing} onClick={() => handleReview('observado')}>
                        Marcar Observado
                      </Button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
