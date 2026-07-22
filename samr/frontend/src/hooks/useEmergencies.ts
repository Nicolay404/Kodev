import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getEmergencies, reportEmergency, dispatchEmergency } from '../services/emergencyService';

export const useEmergencies = () => {
  return useQuery({
    queryKey: ['emergencies'],
    queryFn: getEmergencies,
    refetchInterval: 15000,
  });
};

export const useReportEmergency = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (triageLevel: string) => reportEmergency(triageLevel),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emergencies'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Emergencia reportada. Sigue la guía de primeros auxilios mientras llega ayuda.');
    },
  });
};

export const useDispatchEmergency = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => dispatchEmergency(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emergencies'] });
      toast.success('Emergencia despachada.');
    },
  });
};
