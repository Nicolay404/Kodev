import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { createMatching, type MatchingDto } from '../services/evaluacionService';

export const useCreateMatching = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ evaluacionId, dto }: { evaluacionId: string; dto: MatchingDto }) => createMatching(evaluacionId, dto),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Centro y profesional asignados al caso.');
    },
  });
};
