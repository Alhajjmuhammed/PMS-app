import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '../services/apiServices';

// List all notifications
export const useNotifications = () => {
  return useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list(),
  });
};

// List unread notifications
export const useUnreadNotifications = () => {
  return useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: () => notificationsApi.unread(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

// Get single notification
export const useNotification = (id: number) => {
  return useQuery({
    queryKey: ['notifications', id],
    queryFn: () => notificationsApi.get(id),
    enabled: !!id,
  });
};

// Mark notification as read
export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notifications', 'unread'] });
    },
  });
};
