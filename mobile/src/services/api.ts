import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import { API_URL, TOKEN_KEY, REFRESH_TOKEN_KEY, REQUEST_TIMEOUT } from '../config/env';
import { authEvents } from '../utils/authEvents';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: REQUEST_TIMEOUT,
});

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

// Function to handle token refresh subscribers
const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

// Function to refresh access token
const refreshAccessToken = async (): Promise<string | null> => {
  try {
    const refreshToken = await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      return null;
    }

    const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
      refresh: refreshToken,
    });

    const { access, refresh: newRefresh } = response.data;
    
    if (access) {
      await SecureStore.setItemAsync(TOKEN_KEY, access);
      if (newRefresh) {
        await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, newRefresh);
      }
      return access;
    }
    
    return null;
  } catch (error) {
    console.error('Token refresh failed:', error);
    // Clear tokens on refresh failure
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
    authEvents.emitUnauthorized();
    return null;
  }
};

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

// Response interceptor to handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 errors with token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Wait for token refresh to complete
        return new Promise((resolve) => {
          subscribeTokenRefresh(async (token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Token ${token}`;
            }
            resolve(api(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const newToken = await refreshAccessToken();
      
      if (newToken) {
        isRefreshing = false;
        onRefreshed(newToken);
        
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Token ${newToken}`;
        }
        return api(originalRequest);
      } else {
        isRefreshing = false;
        await SecureStore.deleteItemAsync(TOKEN_KEY);
        await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
        authEvents.emitUnauthorized();
      }
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
  getProfile: () => api.get('/auth/me/'),
  verifyMFA: (mfa_token: string, mfa_code: string) =>
    api.post('/auth/mfa/verify/', { mfa_token, mfa_code }),
};

// Housekeeping API
export const housekeepingApi = {
  getTasks: (params?: { status?: string; date?: string }) =>
    api.get('/housekeeping/tasks/', { params }),
  getMyTasks: () => api.get('/housekeeping/my-tasks/'),
  getTaskDetail: (id: number) => api.get(`/housekeeping/tasks/${id}/`),
  startTask: (id: number) => api.post(`/housekeeping/tasks/${id}/start/`),
  completeTask: (id: number, data?: { notes?: string; photos?: string[] }) =>
    api.post(`/housekeeping/tasks/${id}/complete/`, data),
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
