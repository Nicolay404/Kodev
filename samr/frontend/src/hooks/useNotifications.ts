import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getNotifications, markNotificationRead } from '../services/notificationService';
import { useAuthStore } from '../store/authStore';

export const useNotifications = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return useQuery({
    queryKey: ['notifications'],
    queryFn: getNotifications,
    refetchInterval: 20000,
    enabled: isAuthenticated,
  });
};

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};
