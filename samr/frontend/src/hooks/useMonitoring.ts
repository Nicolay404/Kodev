import { useQuery } from '@tanstack/react-query';
import { getAlerts } from '../services/monitoringService';

export const useAlerts = () => {
  return useQuery({
    queryKey: ['monitoring', 'alerts'],
    queryFn: getAlerts,
    refetchInterval: 15000,
  });
};
