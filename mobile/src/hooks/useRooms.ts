import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roomsApi } from '../services/apiServices';
import { Room } from '../types/api';

// List rooms
export const useRooms = (params?: any) => {
  return useQuery({
    queryKey: ['rooms', params],
    queryFn: () => roomsApi.list(params),
  });
};

// Get single room
export const useRoom = (id: number) => {
  return useQuery({
    queryKey: ['rooms', id],
    queryFn: () => roomsApi.get(id),
    enabled: !!id,
  });
};

// Get available rooms
export const useAvailableRooms = (params: any) => {
  return useQuery({
    queryKey: ['rooms', 'available', params],
    queryFn: () => roomsApi.getAvailable(params),
    enabled: !!params.check_in_date && !!params.check_out_date,
  });
};

// Update room status
export const useUpdateRoomStatus = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      roomsApi.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
    },
  });
};

// Room types
export const useRoomTypes = () => {
  return useQuery({
    queryKey: ['roomTypes'],
    queryFn: () => roomsApi.types.list(),
  });
};
