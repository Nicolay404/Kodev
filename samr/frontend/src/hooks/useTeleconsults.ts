import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createTeleconsultRequest } from '../services/teleconsultService';
import type { CreateRequestDto } from '../services/teleconsultService';
import toast from 'react-hot-toast';

export const useCreateTeleconsultRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateRequestDto) => createTeleconsultRequest(data),
    onSuccess: () => {
      // Invalidar la caché del dashboard para que recargue la tabla
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Solicitud procesada correctamente.');
    },
    // El onError ya está manejado globalmente por el interceptor de Axios
  });
};
