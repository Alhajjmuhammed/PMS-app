import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { guestsApi } from '../services/apiServices';
import { Guest, GuestCreate } from '../types/api';

// List guests
export const useGuests = (params?: any) => {
  return useQuery({
    queryKey: ['guests', params],
    queryFn: () => guestsApi.list(params),
  });
};

// Get single guest
export const useGuest = (id: number) => {
  return useQuery({
    queryKey: ['guests', id],
    queryFn: () => guestsApi.get(id),
    enabled: !!id,
  });
};

// Create guest
export const useCreateGuest = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: GuestCreate) => guestsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guests'] });
    },
  });
};

// Update guest
export const useUpdateGuest = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Guest> }) =>
      guestsApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['guests'] });
      queryClient.invalidateQueries({ queryKey: ['guests', variables.id] });
    },
  });
};

// Search guests
export const useSearchGuests = (query: string) => {
  return useQuery({
    queryKey: ['guests', 'search', query],
    queryFn: () => guestsApi.search(query),
    enabled: query.length >= 2,
  });
};
