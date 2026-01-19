import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { housekeepingApi } from '../services/apiServices';
import { HousekeepingTask } from '../types/api';

// List tasks
export const useHousekeepingTasks = (params?: any) => {
  return useQuery({
    queryKey: ['housekeeping', 'tasks', params],
    queryFn: () => housekeepingApi.tasks.list(params),
  });
};

// Get single task
export const useHousekeepingTask = (id: number) => {
  return useQuery({
    queryKey: ['housekeeping', 'tasks', id],
    queryFn: () => housekeepingApi.tasks.get(id),
    enabled: !!id,
  });
};

// Create task
export const useCreateHousekeepingTask = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<HousekeepingTask>) => housekeepingApi.tasks.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['housekeeping', 'tasks'] });
    },
  });
};

// Update task
export const useUpdateHousekeepingTask = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<HousekeepingTask> }) =>
      housekeepingApi.tasks.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['housekeeping', 'tasks'] });
    },
  });
};

// Complete task
export const useCompleteHousekeepingTask = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => housekeepingApi.tasks.complete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['housekeeping', 'tasks'] });
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
    },
  });
};

// List rooms with status
export const useHousekeepingRooms = (status?: string) => {
  return useQuery({
    queryKey: ['housekeeping', 'rooms', status],
    queryFn: () => housekeepingApi.rooms.list(status),
  });
};

// Update room status
export const useUpdateHousekeepingRoomStatus = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ roomId, status }: { roomId: number; status: string }) =>
      housekeepingApi.rooms.updateStatus(roomId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['housekeeping', 'rooms'] });
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
    },
  });
};
