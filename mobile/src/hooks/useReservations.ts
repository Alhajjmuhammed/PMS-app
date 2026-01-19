import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reservationsApi } from '../services/apiServices';
import { Reservation, ReservationCreate } from '../types/api';

// List reservations
export const useReservations = (params?: any) => {
  return useQuery({
    queryKey: ['reservations', params],
    queryFn: () => reservationsApi.list(params),
  });
};

// Get single reservation
export const useReservation = (id: number) => {
  return useQuery({
    queryKey: ['reservations', id],
    queryFn: () => reservationsApi.get(id),
    enabled: !!id,
  });
};

// Create reservation
export const useCreateReservation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: ReservationCreate) => reservationsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
    },
  });
};

// Update reservation
export const useUpdateReservation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Reservation> }) =>
      reservationsApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      queryClient.invalidateQueries({ queryKey: ['reservations', variables.id] });
    },
  });
};

// Cancel reservation
export const useCancelReservation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) =>
      reservationsApi.cancel(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
    },
  });
};

// Check availability
export const useCheckAvailability = () => {
  return useMutation({
    mutationFn: (data: any) => reservationsApi.checkAvailability(data),
  });
};

// Calculate price
export const useCalculatePrice = () => {
  return useMutation({
    mutationFn: (data: any) => reservationsApi.calculatePrice(data),
  });
};
