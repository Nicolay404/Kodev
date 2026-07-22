import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createSolicitud } from '../services/teleconsultService';
import type { CreateSolicitudDto } from '../services/teleconsultService';
import toast from 'react-hot-toast';

export const useCreateSolicitud = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSolicitudDto) => createSolicitud(data),
    onSuccess: () => {
      // Invalidar la caché del dashboard para que recargue la tabla
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Solicitud enviada. Un profesional la evaluará en breve.');
    },
    // El onError ya está manejado globalmente por el interceptor de Axios (gatewayClient)
  });
};
