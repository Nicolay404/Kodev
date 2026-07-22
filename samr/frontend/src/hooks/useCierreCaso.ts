import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getCasos, verifyCaso, closeCaso } from '../services/cierreCasoService';

export const useCasos = () => {
  return useQuery({ queryKey: ['casos'], queryFn: getCasos });
};

export const useVerifyCaso = (casoId: string | null) => {
  return useQuery({
    queryKey: ['casos', casoId, 'verify'],
    queryFn: () => verifyCaso(casoId as string),
    enabled: !!casoId,
  });
};

export const useCloseCaso = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ casoId, clinicalNotes }: { casoId: string; clinicalNotes: string }) => closeCaso(casoId, clinicalNotes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['casos'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Caso cerrado correctamente.');
    },
  });
};
