import { useState } from 'react';
import { Activity, Stethoscope, FolderCheck, FolderOpen, Siren, Video, Bell, FileText } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { NewRequestModal } from './NewRequestModal';
import { ViewRequestModal } from './ViewRequestModal';
import { useDashboard } from '../../hooks/useDashboard';
import { useAuthStore } from '../../store/authStore';
import { asList, isBackendError, type Evaluacion } from '../../services/dashboardService';

const RISK_LABEL: Record<Evaluacion['nivel_riesgo'], string> = {
  critico: 'Crítico',
  alto: 'Alto',
  medio: 'Medio',
  bajo: 'Bajo',
};

const RISK_STYLE: Record<Evaluacion['nivel_riesgo'], string> = {
  critico: 'bg-error-50 text-error-700 border-error-200',
  alto: 'bg-warning-50 text-warning-700 border-warning-200',
  medio: 'bg-info-50 text-info-700 border-info-200',
  bajo: 'bg-success-50 text-success-700 border-success-200',
};

interface StatCard {
  label: string;
  value: number | string;
  icon: LucideIcon;
  color: string;
  bg: string;
  hint?: string;
}

export function Dashboard() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState<Evaluacion | null>(null);
  const role = useAuthStore((state) => state.user?.role);

  const { data, isLoading } = useDashboard();

  const solicitudes = asList(data?.solicitudes);
  const evaluaciones = asList(data?.evaluacion);
  const alertas = asList(data?.monitoring);
  const casos = asList(data?.atencion);
  const emergencias = asList(data?.emergencias);
  const teleconsultas = asList(data?.teleconsultas);
  const notificaciones = asList(data?.notificaciones);
  const monitoringBlocked = data ? isBackendError(data.monitoring) : false;

  const statCards: StatCard[] = [];
  if (data?.solicitudes !== undefined) {
    statCards.push({ label: 'Mis Solicitudes', value: solicitudes.length, icon: FileText, color: 'text-info-600', bg: 'bg-info-50' });
  }
  if (data?.evaluacion !== undefined) {
    statCards.push({ label: 'Casos Evaluados', value: evaluaciones.length, icon: Stethoscope, color: 'text-info-600', bg: 'bg-info-50' });
  }
  if (data?.monitoring !== undefined) {
    statCards.push({
      label: 'Alertas de Monitoreo',
      value: monitoringBlocked ? '—' : alertas.length,
      icon: Activity,
      color: 'text-error-600',
      bg: 'bg-error-50',
      hint: monitoringBlocked ? 'No disponible para tu rol' : undefined,
    });
  }
  if (data?.atencion !== undefined) {
    statCards.push({ label: 'Casos Abiertos', value: casos.filter((c) => c.status === 'open').length, icon: FolderOpen, color: 'text-warning-600', bg: 'bg-warning-50' });
    statCards.push({ label: 'Casos Cerrados', value: casos.filter((c) => c.status === 'closed').length, icon: FolderCheck, color: 'text-success-600', bg: 'bg-success-50' });
  }
  if (data?.emergencias !== undefined) {
    statCards.push({ label: 'Emergencias', value: emergencias.length, icon: Siren, color: 'text-error-600', bg: 'bg-error-50' });
  }
  if (data?.teleconsultas !== undefined) {
    statCards.push({ label: 'Teleconsultas', value: teleconsultas.length, icon: Video, color: 'text-teal-600', bg: 'bg-teal-50' });
  }
  if (data?.notificaciones !== undefined) {
    statCards.push({ label: 'Notificaciones', value: notificaciones.length, icon: Bell, color: 'text-gray-600', bg: 'bg-gray-100' });
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard General</h1>
          <p className="text-gray-600 text-sm">Resumen de actividad del Sistema de Atención Médica Remota.</p>
        </div>
        {role === 'patient' && (
          <Button onClick={() => setIsModalOpen(true)}>Nueva Solicitud</Button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-surface p-6 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
              <Skeleton className="w-12 h-12 rounded-full" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-6 w-12" />
              </div>
            </div>
          ))
        ) : (
          statCards.map((stat, i) => (
            <div key={i} className="bg-surface p-6 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${stat.bg} ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                {stat.hint && <p className="text-xs text-gray-400">{stat.hint}</p>}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Rol clínico (professional/center_admin): casos evaluados recientemente */}
      {role !== 'patient' && data?.evaluacion !== undefined && (
        <div className="bg-surface rounded-lg shadow-sm border border-gray-200 mt-8 overflow-hidden">
          <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50/50">
            <h2 className="text-lg font-semibold text-gray-900">Casos Recientes</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white border-b border-gray-200">
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">ID / Fecha</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Nivel de Riesgo</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">Acción</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {evaluaciones.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-6 py-8 text-center text-gray-500">
                      No hay casos evaluados recientes.
                    </td>
                  </tr>
                ) : (
                  evaluaciones.map((caso) => (
                    <tr key={caso.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{caso.id.slice(0, 8)}</div>
                        <div className="text-xs text-gray-500">{new Date(caso.created_at).toLocaleString()}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${RISK_STYLE[caso.nivel_riesgo]}`}>
                          {RISK_LABEL[caso.nivel_riesgo]}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <Button variant="outline" size="sm" onClick={() => setSelectedCase(caso)}>
                          Ver Caso
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Rol patient: mis solicitudes */}
      {role === 'patient' && (
        <div className="bg-surface rounded-lg shadow-sm border border-gray-200 mt-8 overflow-hidden">
          <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50/50">
            <h2 className="text-lg font-semibold text-gray-900">Mis Solicitudes</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white border-b border-gray-200">
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Síntomas</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {solicitudes.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-6 py-8 text-center text-gray-500">
                      No has enviado solicitudes aún.
                    </td>
                  </tr>
                ) : (
                  solicitudes.map((s) => (
                    <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(s.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">{s.sintomas.join(', ')}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 capitalize">{s.estado}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <NewRequestModal open={isModalOpen} onOpenChange={setIsModalOpen} />

      <ViewRequestModal evaluacion={selectedCase} onClose={() => setSelectedCase(null)} />
    </div>
  );
}
