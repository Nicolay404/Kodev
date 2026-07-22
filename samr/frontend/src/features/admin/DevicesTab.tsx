import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useDevices, useRegisterDevice } from '../../hooks/useAdmin';

export function DevicesTab() {
  const { data: devices, isLoading } = useDevices();
  const { mutate: register, isPending } = useRegisterDevice();
  const [formOpen, setFormOpen] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fd = new FormData(form);
    register(
      {
        patient_id: fd.get('patient_id') as string,
        device_type: fd.get('device_type') as string,
        serial_number: fd.get('serial_number') as string,
      },
      { onSuccess: () => { setFormOpen(false); form.reset(); } }
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button size="sm" onClick={() => setFormOpen((v) => !v)}>
          <Plus className="w-4 h-4 mr-1" /> Registrar Dispositivo
        </Button>
      </div>

      {formOpen && (
        <form onSubmit={handleSubmit} className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
          <p className="text-xs text-gray-500">
            El `serial_number` viaja en el evento de alta pero no se persiste (no forma parte del esquema `devices` aprobado).
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input name="patient_id" required placeholder="ID del paciente (UUID)" className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
            <input name="device_type" required placeholder="Tipo (ej. BioMonitor X1)" className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
            <input name="serial_number" required placeholder="Número de serie" className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
          </div>
          <Button type="submit" size="sm" disabled={isPending}>{isPending ? 'Registrando...' : 'Confirmar Registro'}</Button>
        </form>
      )}

      <div className="bg-surface rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Paciente</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <tr key={i}><td className="px-6 py-4" colSpan={3}><Skeleton className="h-4 w-full" /></td></tr>
                ))
              ) : !devices || devices.length === 0 ? (
                <tr><td colSpan={3} className="px-6 py-8 text-center text-gray-500">No hay dispositivos registrados.</td></tr>
              ) : (
                devices.map((d) => (
                  <tr key={d.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{d.patient_id.slice(0, 8)}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{d.device_type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${d.active ? 'bg-success-50 text-success-700 border-success-200' : 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                        {d.active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
