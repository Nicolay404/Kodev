import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Clock, Users, CheckCircle, ArrowRight } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { NewRequestModal } from './NewRequestModal';
import { ViewRequestModal } from './ViewRequestModal';
import { useDashboard } from '../../hooks/useDashboard';
import type { TeleconsultRequest } from '../../services/dashboardService';

export function Dashboard() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<TeleconsultRequest | null>(null);

  const { data, isLoading } = useDashboard();

  // Mapeamos los datos reales del BFF. Si no hay data (loading o error), usamos valores por defecto
  const stats = data?.stats || { active: 0, pending: 0, resolved: 0, totalPatients: 0 };
  const requests = data?.recentRequests || [];

  const handleNewRequest = () => {
    // Ya no manejamos el estado local aquí.
    // El onSucess del useCreateTeleconsultRequest (React Query)
    // llamará a invalidateQueries y recargará automáticamente el useDashboard().
  };

  const statCards = [
    { label: 'Consultas Activas', value: stats.active, icon: Activity, color: 'text-info-600', bg: 'bg-info-50' },
    { label: 'En Espera', value: stats.pending, icon: Clock, color: 'text-warning-600', bg: 'bg-warning-50' },
    { label: 'Resueltas (Mes)', value: stats.resolved, icon: CheckCircle, color: 'text-success-600', bg: 'bg-success-50' },
    { label: 'Pacientes Totales', value: stats.totalPatients, icon: Users, color: 'text-teal-600', bg: 'bg-teal-50' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard General</h1>
          <p className="text-gray-600 text-sm">Resumen de actividad del Sistema de Atención Médica Remota.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          Nueva Solicitud
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          // Skeletons
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
          // Datos reales (simulados)
          statCards.map((stat, i) => (
            <div key={i} className="bg-surface p-6 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${stat.bg} ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Tabla de Solicitudes Recientes */}
      <div className="bg-surface rounded-lg shadow-sm border border-gray-200 mt-8 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50/50">
          <h2 className="text-lg font-semibold text-gray-900">Solicitudes Recientes</h2>
          <Button variant="ghost" size="sm" className="text-teal-600 flex items-center gap-1" onClick={() => navigate('/patients')}>
            Ver todas <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white border-b border-gray-200">
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">ID / Hora</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Paciente</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Motivo</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {isLoading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-20" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-48" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-6 w-24 rounded-full" /></td>
                    <td className="px-6 py-4 text-right"><Skeleton className="h-8 w-20 ml-auto" /></td>
                  </tr>
                ))
              ) : requests.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No hay solicitudes recientes.
                  </td>
                </tr>
              ) : (
                requests.map((req) => (
                  <tr key={req.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{req.id}</div>
                      <div className="text-xs text-gray-500">{req.time}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{req.patient}</div>
                      <div className="text-xs text-gray-500">CC: {req.cedula}</div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-600 line-clamp-2 max-w-xs">{req.reason}</p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {req.status === 'En Espera' ? (
                        <span className="px-2.5 py-1 bg-warning-50 text-warning-700 text-xs font-medium rounded-full border border-warning-200">
                          En Espera
                        </span>
                      ) : req.status === 'Resuelto' ? (
                        <span className="px-2.5 py-1 bg-success-50 text-success-700 text-xs font-medium rounded-full border border-success-200">
                          Resuelto
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 bg-info-50 text-info-700 text-xs font-medium rounded-full border border-info-200">
                          En Atención
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right flex gap-2 justify-end">
                      {req.status === 'En Espera' && (
                        <Button variant="primary" size="sm" onClick={() => navigate('/teleconsult')}>
                          Atender
                        </Button>
                      )}
                      <Button variant="outline" size="sm" onClick={() => setSelectedRequest(req)}>
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

      <NewRequestModal 
        open={isModalOpen} 
        onOpenChange={setIsModalOpen}
        onSuccess={handleNewRequest}
      />
      
      <ViewRequestModal 
        request={selectedRequest}
        onClose={() => setSelectedRequest(null)}
      />
    </div>
  );
}
