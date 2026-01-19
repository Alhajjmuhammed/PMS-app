import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { API_URL, TOKEN_KEY, REQUEST_TIMEOUT } from '../config/env';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: REQUEST_TIMEOUT,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await SecureStore.deleteItemAsync(TOKEN_KEY);
      // Navigate to login
    }
    
    // Format error message
    const errorMessage = error.response?.data?.message 
      || error.response?.data?.detail 
      || error.message 
      || 'An unexpected error occurred';
    
    return Promise.reject({
      ...error,
      message: errorMessage,
      statusCode: error.response?.status,
    });
  }
);

export default api;

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),
  logout: () => api.post('/auth/logout/'),
  getProfile: () => api.get('/auth/profile/'),
};

// Housekeeping API
export const housekeepingApi = {
  getTasks: (params?: { status?: string; date?: string }) =>
    api.get('/housekeeping/tasks/', { params }),
  getMyTasks: () => api.get('/housekeeping/my-tasks/'),
  getTaskDetail: (id: number) => api.get(`/housekeeping/tasks/${id}/`),
  startTask: (id: number) => api.post(`/housekeeping/tasks/${id}/start/`),
  completeTask: (id: number, notes?: string) =>
    api.post(`/housekeeping/tasks/${id}/complete/`, { notes }),
  getRoomStatus: (floor?: number) =>
    api.get('/housekeeping/rooms/', { params: { floor } }),
};

// Maintenance API
export const maintenanceApi = {
  getRequests: (params?: { status?: string; priority?: string }) =>
    api.get('/maintenance/requests/', { params }),
  getMyRequests: () => api.get('/maintenance/my-requests/'),
  getRequestDetail: (id: number) => api.get(`/maintenance/requests/${id}/`),
  createRequest: (data: any) => api.post('/maintenance/requests/create/', data),
  startRequest: (id: number) => api.post(`/maintenance/requests/${id}/start/`),
  completeRequest: (id: number, data: any) =>
    api.post(`/maintenance/requests/${id}/complete/`, data),
};

// Front Desk API
export const frontdeskApi = {
  getDashboard: () => api.get('/frontdesk/dashboard/'),
  checkIn: (data: any) => api.post('/frontdesk/check-in/', data),
  checkOut: (data: any) => api.post('/frontdesk/check-out/', data),
};

// Rooms API
export const roomsApi = {
  getRooms: (params?: { status?: string; floor?: number }) =>
    api.get('/rooms/', { params }),
  getRoomDetail: (id: number) => api.get(`/rooms/${id}/`),
  updateRoomStatus: (id: number, data: any) =>
    api.post(`/rooms/${id}/status/`, data),
  getAvailability: (checkIn: string, checkOut: string) =>
    api.get('/rooms/availability/', { params: { check_in: checkIn, check_out: checkOut } }),
};

// Reports API
export const reportsApi = {
  getDashboardStats: () => api.get('/reports/dashboard/'),
};
