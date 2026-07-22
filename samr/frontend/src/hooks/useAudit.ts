import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getAuditDecisions, reviewAuditDecision, type AuditFilters } from '../services/auditService';

export const useAuditDecisions = (filters: AuditFilters) => {
  return useQuery({
    queryKey: ['audit', 'decisions', filters],
    queryFn: () => getAuditDecisions(filters),
  });
};

export const useReviewAuditDecision = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, estado, comentario }: { id: number; estado: 'revisado' | 'observado'; comentario?: string }) =>
      reviewAuditDecision(id, estado, comentario),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit', 'decisions'] });
      toast.success('Revisión registrada.');
    },
  });
};
