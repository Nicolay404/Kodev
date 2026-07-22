import { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X, Check, XIcon, Link2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAuthStore } from '../../store/authStore';
import { useCasos, useVerifyCaso, useCloseCaso } from '../../hooks/useCierreCaso';
import type { Caso } from '../../services/cierreCasoService';

const STATUS_STYLE: Record<Caso['status'], string> = {
  open: 'bg-warning-50 text-warning-700 border-warning-200',
  closed: 'bg-success-50 text-success-700 border-success-200',
};

function Readiness({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className={`flex items-center gap-2 text-sm ${ok ? 'text-success-700' : 'text-gray-400'}`}>
      {ok ? <Check className="w-4 h-4" /> : <XIcon className="w-4 h-4" />}
      {label}
    </div>
  );
}

export function CierreCasoList() {
  const role = useAuthStore((state) => state.user?.role);
  const { data: casos, isLoading } = useCasos();
  const [selected, setSelected] = useState<Caso | null>(null);
  const [notes, setNotes] = useState('');
  const { data: readiness, isLoading: verifying } = useVerifyCaso(selected?.id ?? null);
  const { mutate: close, isPending: closing } = useCloseCaso();

  const handleClose = () => {
    if (!selected) return;
    close(
      { casoId: selected.id, clinicalNotes: notes },
      { onSuccess: () => { setSelected(null); setNotes(''); } }
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cierre de Casos</h1>
        <p className="text-gray-600 text-sm">
          {role === 'patient' ? 'Tus casos clínicos.' : 'Todos los casos — verifica y cierra con notas clínicas.'}
        </p>
      </div>

      <div className="bg-surface rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                {role !== 'patient' && <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Paciente</th>}
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Origen</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i}><td className="px-6 py-4" colSpan={4}><Skeleton className="h-4 w-full" /></td></tr>
                ))
              ) : !casos || casos.length === 0 ? (
                <tr><td colSpan={4} className="px-6 py-8 text-center text-gray-500">No hay casos registrados.</td></tr>
              ) : (
                casos.map((caso) => (
                  <tr key={caso.id} className="hover:bg-gray-50">
                    {role !== 'patient' && (
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{caso.patient_id.slice(0, 8)}</td>
                    )}
                    <td className="px-6 py-4 text-sm text-gray-500 flex items-center gap-1">
                      <Link2 className="w-3 h-3" />
                      {caso.teleconsult_id ? 'Teleconsulta' : caso.emergency_id ? 'Emergencia' : '—'}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${STATUS_STYLE[caso.status]}`}>
                        {caso.status === 'open' ? 'Abierto' : 'Cerrado'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button variant="outline" size="sm" onClick={() => { setSelected(caso); setNotes(caso.clinical_notes || ''); }}>
                        Ver
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Dialog.Root open={!!selected} onOpenChange={(open) => !open && setSelected(null)}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] bg-surface rounded-lg shadow-lg p-6 animate-in fade-in zoom-in duration-200">
            {selected && (
              <>
                <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-4">
                  <Dialog.Title className="text-lg font-bold text-gray-900">Caso {selected.id.slice(0, 8)}</Dialog.Title>
                  <Dialog.Close asChild>
                    <button className="text-gray-400 hover:text-gray-600 p-1" aria-label="Cerrar"><X className="w-5 h-5" /></button>
                  </Dialog.Close>
                </div>

                <div className="space-y-4 text-sm">
                  {selected.status === 'closed' ? (
                    <div className="bg-success-50 border border-success-100 rounded-lg p-3">
                      <p className="text-gray-900">{selected.clinical_notes}</p>
                      <p className="text-xs text-gray-400 mt-1">Cerrado el {selected.closed_at ? new Date(selected.closed_at).toLocaleString() : ''}</p>
                    </div>
                  ) : (
                    <>
                      {role !== 'patient' && (
                        <div className="bg-gray-50 border border-gray-100 rounded-lg p-3 space-y-1">
                          <p className="text-xs font-medium text-gray-500 uppercase mb-2">Verificación de completitud</p>
                          {verifying ? (
                            <Skeleton className="h-16 w-full" />
                          ) : readiness ? (
                            <>
                              <Readiness label="Tiene notas clínicas" ok={readiness.has_clinical_notes} />
                              <Readiness label="Tiene fuente de atención (teleconsulta/emergencia)" ok={readiness.has_attention_source} />
                              <Readiness label="Listo para cerrar" ok={readiness.ready_to_close} />
                            </>
                          ) : null}
                        </div>
                      )}

                      {role === 'professional' ? (
                        <div className="space-y-2">
                          <label className="block text-sm font-medium text-gray-700">Notas clínicas de cierre</label>
                          <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            rows={4}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                            placeholder="Diagnóstico, tratamiento indicado, observaciones..."
                          />
                          <Button className="w-full" disabled={closing || !notes.trim()} onClick={handleClose}>
                            {closing ? 'Cerrando...' : 'Cerrar Caso'}
                          </Button>
                        </div>
                      ) : (
                        <p className="text-gray-500 text-xs">Solo un profesional puede cerrar el caso.</p>
                      )}
                    </>
                  )}
                </div>
              </>
            )}
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
