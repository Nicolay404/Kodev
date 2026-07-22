import { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { Siren, X, ShieldAlert, Send } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAuthStore } from '../../store/authStore';
import { useEmergencies, useReportEmergency, useDispatchEmergency } from '../../hooks/useEmergencies';
import type { Emergency } from '../../services/emergencyService';

const STATUS_LABEL: Record<Emergency['status'], string> = {
  pending: 'Pendiente',
  dispatched: 'Despachada',
  closed: 'Cerrada',
};

const STATUS_STYLE: Record<Emergency['status'], string> = {
  pending: 'bg-error-50 text-error-700 border-error-200',
  dispatched: 'bg-warning-50 text-warning-700 border-warning-200',
  closed: 'bg-success-50 text-success-700 border-success-200',
};

const TRIAGE_LEVELS = [
  { value: 'critico', label: 'Crítico' },
  { value: 'alto', label: 'Alto' },
  { value: 'medio', label: 'Medio' },
  { value: 'bajo', label: 'Bajo' },
];

const CAN_DISPATCH: string[] = ['professional', 'nurse', 'center_admin', 'system_admin'];

export function EmergenciesList() {
  const role = useAuthStore((state) => state.user?.role);
  const { data: emergencies, isLoading } = useEmergencies();
  const { mutate: report, isPending: reporting } = useReportEmergency();
  const { mutate: dispatch, isPending: dispatching } = useDispatchEmergency();

  const [selected, setSelected] = useState<Emergency | null>(null);
  const [reportOpen, setReportOpen] = useState(false);
  const [triageLevel, setTriageLevel] = useState('alto');

  const handleReport = (e: React.FormEvent) => {
    e.preventDefault();
    report(triageLevel, { onSuccess: () => setReportOpen(false) });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Emergencias</h1>
          <p className="text-gray-600 text-sm">
            {role === 'patient' ? 'Tus emergencias reportadas.' : 'Cola de emergencias de todos los pacientes.'}
          </p>
        </div>
        {role === 'patient' && (
          <Button onClick={() => setReportOpen(true)} className="bg-error-600 hover:bg-error-700 border-error-600 hover:border-error-700">
            <Siren className="w-4 h-4 mr-2" /> Reportar Emergencia
          </Button>
        )}
      </div>

      <div className="bg-surface rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                {role !== 'patient' && <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Paciente</th>}
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Nivel de Triaje</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Reportada</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4" colSpan={5}><Skeleton className="h-4 w-full" /></td>
                  </tr>
                ))
              ) : !emergencies || emergencies.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">No hay emergencias registradas.</td>
                </tr>
              ) : (
                emergencies.map((em) => (
                  <tr key={em.id} className="hover:bg-gray-50 transition-colors">
                    {role !== 'patient' && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{em.patient_id.slice(0, 8)}</td>
                    )}
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 capitalize">{em.triage_level}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${STATUS_STYLE[em.status]}`}>
                        {STATUS_LABEL[em.status]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">
                      {new Date(em.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <Button variant="outline" size="sm" onClick={() => setSelected(em)}>Ver</Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detalle + guía de primeros auxilios + despacho */}
      <Dialog.Root open={!!selected} onOpenChange={(open) => !open && setSelected(null)}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] bg-surface rounded-lg shadow-lg p-6 animate-in fade-in zoom-in duration-200">
            {selected && (
              <>
                <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-4">
                  <Dialog.Title className="text-lg font-bold text-gray-900">Emergencia {selected.id.slice(0, 8)}</Dialog.Title>
                  <Dialog.Close asChild>
                    <button className="text-gray-400 hover:text-gray-600 p-1" aria-label="Cerrar"><X className="w-5 h-5" /></button>
                  </Dialog.Close>
                </div>
                <div className="space-y-4 text-sm">
                  <div className="flex items-center gap-3">
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${STATUS_STYLE[selected.status]}`}>
                      {STATUS_LABEL[selected.status]}
                    </span>
                    <span className="text-gray-500 capitalize">Triaje: {selected.triage_level}</span>
                  </div>

                  {selected.guides.map((guide) => (
                    <div key={guide.id} className="bg-info-50 border border-info-200 rounded-lg p-4">
                      <h3 className="text-sm font-bold text-info-800 flex items-center gap-2 mb-2">
                        <ShieldAlert className="w-4 h-4" /> Guía de Primeros Auxilios
                      </h3>
                      <p className="text-info-700">{guide.contenido}</p>
                      <p className="text-xs text-info-500 mt-2">
                        Guía no clínica generada automáticamente — no sustituye atención profesional.
                      </p>
                    </div>
                  ))}

                  {role && CAN_DISPATCH.includes(role) && selected.status === 'pending' && (
                    <Button
                      className="w-full"
                      disabled={dispatching}
                      onClick={() => dispatch(selected.id, { onSuccess: () => setSelected(null) })}
                    >
                      {dispatching ? 'Despachando...' : 'Despachar Emergencia'}
                    </Button>
                  )}
                </div>
              </>
            )}
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      {/* Reportar nueva emergencia (patient) */}
      <Dialog.Root open={reportOpen} onOpenChange={setReportOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 transition-opacity" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-sm translate-x-[-50%] translate-y-[-50%] bg-surface rounded-lg shadow-lg p-6 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between mb-4">
              <Dialog.Title className="text-lg font-bold text-gray-900">Reportar Emergencia</Dialog.Title>
              <Dialog.Close asChild>
                <button className="text-gray-400 hover:text-gray-600" aria-label="Cerrar"><X className="w-5 h-5" /></button>
              </Dialog.Close>
            </div>
            <form onSubmit={handleReport} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nivel de urgencia percibido</label>
                <select
                  value={triageLevel}
                  onChange={(e) => setTriageLevel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
                >
                  {TRIAGE_LEVELS.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
              <Button type="submit" className="w-full bg-error-600 hover:bg-error-700 border-error-600 hover:border-error-700" disabled={reporting}>
                <Send className="w-4 h-4 mr-2" /> {reporting ? 'Enviando...' : 'Reportar Ahora'}
              </Button>
            </form>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
