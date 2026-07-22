import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getMyProfile, updateMyProfile, type PatientProfileDto } from '../services/patientProfileService';
import { useAuthStore } from '../store/authStore';

export const useMyProfile = () => {
  const role = useAuthStore((state) => state.user?.role);
  return useQuery({
    queryKey: ['patient-profile'],
    queryFn: getMyProfile,
    enabled: role === 'patient',
    retry: false,
  });
};

export const useUpdateMyProfile = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (dto: PatientProfileDto) => updateMyProfile(dto),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patient-profile'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Perfil actualizado.');
    },
  });
};
