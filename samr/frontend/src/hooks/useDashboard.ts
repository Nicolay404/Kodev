import { useQuery } from '@tanstack/react-query';
import { getDashboardData } from '../services/dashboardService';

export const useDashboard = () => {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardData,
    refetchInterval: 30000, // Actualizar automáticamente cada 30 segundos
    retry: 2, // Reintentar 2 veces en caso de error
  });
};
