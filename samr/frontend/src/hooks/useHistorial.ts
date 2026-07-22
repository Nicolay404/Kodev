import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getHistorial, addClinicalNote } from '../services/historialService';

export const useHistorial = (patientId: string | undefined) => {
  return useQuery({
    queryKey: ['historial', patientId],
    queryFn: () => getHistorial(patientId as string),
    enabled: !!patientId,
    retry: false,
  });
};

export const useAddClinicalNote = (patientId: string | undefined) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (note: string) => addClinicalNote(patientId as string, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['historial', patientId] });
      toast.success('Nota clínica agregada.');
    },
  });
};
