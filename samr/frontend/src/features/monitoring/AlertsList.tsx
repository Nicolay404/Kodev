import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, ArrowRight } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAlerts } from '../../hooks/useMonitoring';
import type { Alert } from '../../services/dashboardService';

const SEVERITY_LABEL: Record<Alert['severity'], string> = {
  critical: 'Crítica',
  high: 'Alta',
  medium: 'Media',
  low: 'Baja',
};

const SEVERITY_STYLE: Record<Alert['severity'], string> = {
  critical: 'bg-error-50 text-error-700 border-error-200',
  high: 'bg-warning-50 text-warning-700 border-warning-200',
  medium: 'bg-info-50 text-info-700 border-info-200',
  low: 'bg-success-50 text-success-700 border-success-200',
};

/**
 * No existe en el backend un endpoint de "listado de pacientes" (patient-service
 * solo expone /me/ para el propio paciente y /summary/ vía token de servicio,
 * no JWT de usuario). La lista más cercana con datos reales de varios pacientes
 * es la cola de alertas de monitoreo (GET /api/monitoring/alerts/).
 */
export function AlertsList() {
  const { data: alerts, isLoading } = useAlerts();
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const filtered = useMemo(() => {
    return (alerts || []).filter((a) => {
      const matchesSearch = a.patient_id.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesSeverity = severityFilter === 'all' || a.severity === severityFilter;
      return matchesSearch && matchesSeverity;
    });
  }, [alerts, searchQuery, severityFilter]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Alertas de Monitoreo</h1>
        <p className="text-gray-600 text-sm">Últimas 50 alertas detectadas por monitoring-service, de todos los pacientes.</p>
      </div>

      <div className="bg-surface rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="relative flex-1 w-full max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Buscar por ID de paciente..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              className="border border-gray-300 rounded-md py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="all">Toda severidad</option>
              <option value="critical">Crítica</option>
              <option value="high">Alta</option>
              <option value="medium">Media</option>
              <option value="low">Baja</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Paciente (ID)</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Severidad</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Detectada</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-6 w-20 rounded-full" /></td>
                    <td className="px-6 py-4 hidden sm:table-cell"><Skeleton className="h-4 w-24" /></td>
                    <td className="px-6 py-4 text-right"><Skeleton className="h-8 w-20 ml-auto" /></td>
                  </tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                    No hay alertas activas.
                  </td>
                </tr>
              ) : (
                filtered.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {alert.patient_id.slice(0, 8)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${SEVERITY_STYLE[alert.severity]}`}>
                        {SEVERITY_LABEL[alert.severity]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">
                      {new Date(alert.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <Button variant="outline" size="sm" onClick={() => navigate(`/monitoring/${alert.patient_id}`)}>
                        Ver en vivo <ArrowRight className="w-4 h-4 ml-1" />
                      </Button>
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
