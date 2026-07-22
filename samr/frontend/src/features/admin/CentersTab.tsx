import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useCenters, useRegisterCenter } from '../../hooks/useAdmin';
import type { Center } from '../../services/adminService';

const STATUS_LABEL: Record<Center['status'], string> = {
  pending_validation: 'Validación pendiente',
  validated: 'Validado',
  rejected: 'Rechazado',
};

const STATUS_STYLE: Record<Center['status'], string> = {
  pending_validation: 'bg-warning-50 text-warning-700 border-warning-200',
  validated: 'bg-success-50 text-success-700 border-success-200',
  rejected: 'bg-error-50 text-error-700 border-error-200',
};

export function CentersTab() {
  const [statusFilter, setStatusFilter] = useState('');
  const { data: centers, isLoading } = useCenters(statusFilter || undefined);
  const { mutate: register, isPending } = useRegisterCenter();
  const [formOpen, setFormOpen] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fd = new FormData(form);
    register(
      {
        name: fd.get('name') as string,
        type: fd.get('type') as string,
        license_number: fd.get('license_number') as string,
        specialties: (fd.get('specialties') as string).split(',').map((s) => s.trim()).filter(Boolean),
      },
      { onSuccess: () => { setFormOpen(false); form.reset(); } }
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-gray-300 rounded-md py-2 px-3 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
        >
          <option value="">Todos los estados</option>
          <option value="pending_validation">Validación pendiente</option>
          <option value="validated">Validado</option>
          <option value="rejected">Rechazado</option>
        </select>
        <Button size="sm" onClick={() => setFormOpen((v) => !v)}>
          <Plus className="w-4 h-4 mr-1" /> Registrar Centro
        </Button>
      </div>

      {formOpen && (
        <form onSubmit={handleSubmit} className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input name="name" required placeholder="Nombre del centro" className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
            <input name="type" required placeholder="Tipo (ej. hospital)" className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
            <input name="license_number" required placeholder="Número de licencia" className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
            <input name="specialties" required placeholder="Especialidades (separadas por coma)" className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
          </div>
          <Button type="submit" size="sm" disabled={isPending}>{isPending ? 'Registrando...' : 'Confirmar Registro'}</Button>
        </form>
      )}

      <div className="bg-surface rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <tr key={i}><td className="px-6 py-4" colSpan={3}><Skeleton className="h-4 w-full" /></td></tr>
                ))
              ) : !centers || centers.length === 0 ? (
                <tr><td colSpan={3} className="px-6 py-8 text-center text-gray-500">No hay centros registrados.</td></tr>
              ) : (
                centers.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{c.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{c.type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${STATUS_STYLE[c.status]}`}>
                        {STATUS_LABEL[c.status]}
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
