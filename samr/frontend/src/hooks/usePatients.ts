import { useQuery } from '@tanstack/react-query';
import { getPatients, getPatientSummary } from '../services/patientService';

export const usePatients = () => {
  return useQuery({
    queryKey: ['patients'],
    queryFn: getPatients,
  });
};

export const usePatientSummary = (patientId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['patients', patientId, 'summary'],
    queryFn: () => getPatientSummary(patientId),
    enabled: !!patientId && enabled,
  });
};
