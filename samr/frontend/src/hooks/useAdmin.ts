import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  getCenters, registerCenter, getDevices, registerDevice, getFAQs, createFAQ, updateFAQ,
  type RegisterCenterDto, type RegisterDeviceDto,
} from '../services/adminService';

export const useCenters = (status?: string) => {
  return useQuery({ queryKey: ['admin', 'centers', status ?? 'all'], queryFn: () => getCenters(status) });
};

export const useRegisterCenter = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (dto: RegisterCenterDto) => registerCenter(dto),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'centers'] });
      toast.success('Centro registrado. Validación M2M en curso.');
    },
  });
};

export const useDevices = () => {
  return useQuery({ queryKey: ['admin', 'devices'], queryFn: getDevices });
};

export const useRegisterDevice = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (dto: RegisterDeviceDto) => registerDevice(dto),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'devices'] });
      toast.success('Dispositivo registrado.');
    },
  });
};

export const useFAQs = () => {
  return useQuery({ queryKey: ['admin', 'faq'], queryFn: getFAQs });
};

export const useCreateFAQ = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ question, answer }: { question: string; answer: string }) => createFAQ(question, answer),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'faq'] });
      toast.success('FAQ creada.');
    },
  });
};

export const useUpdateFAQ = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, question, answer }: { id: string; question: string; answer: string }) => updateFAQ(id, question, answer),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'faq'] });
      toast.success('FAQ actualizada.');
    },
  });
};
