import { useQuery } from '@tanstack/react-query';
import { reportsApi } from '../services/apiServices';

// Dashboard stats
export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['reports', 'dashboard'],
    queryFn: () => reportsApi.dashboard(),
    refetchInterval: 60000, // Refetch every minute
  });
};

// Occupancy report
export const useOccupancyReport = (params: any) => {
  return useQuery({
    queryKey: ['reports', 'occupancy', params],
    queryFn: () => reportsApi.occupancy(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};

// Revenue report
export const useRevenueReport = (params: any) => {
  return useQuery({
    queryKey: ['reports', 'revenue', params],
    queryFn: () => reportsApi.revenue(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};

// Daily statistics
export const useDailyStats = (date: string) => {
  return useQuery({
    queryKey: ['reports', 'daily', date],
    queryFn: () => reportsApi.dailyStats(date),
    enabled: !!date,
  });
};
