import api from './api';

// Properties API
export const propertiesApi = {
  list: () => api.get('/properties/'),
  get: (id: number) => api.get(`/properties/${id}/`),
  create: (data: any) => api.post('/properties/', data),
  update: (id: number, data: any) => api.patch(`/properties/${id}/`, data),
  delete: (id: number) => api.delete(`/properties/${id}/`),
};

// Rooms API
export const roomsApi = {
  list: (params?: any) => api.get('/rooms/', { params }),
  get: (id: number) => api.get(`/rooms/${id}/`),
  getAvailable: (params: any) => api.get('/rooms/available/', { params }),
  updateStatus: (id: number, status: string) => api.post(`/rooms/${id}/status/`, { status }),
  
  // Room Types
  types: {
    list: () => api.get('/rooms/types/'),
    get: (id: number) => api.get(`/rooms/types/${id}/`),
  },
};

// Reservations API
export const reservationsApi = {
  list: (params?: any) => api.get('/reservations/', { params }),
  get: (id: number) => api.get(`/reservations/${id}/`),
  create: (data: any) => api.post('/reservations/', data),
  update: (id: number, data: any) => api.patch(`/reservations/${id}/`, data),
  cancel: (id: number, reason: string) => api.post(`/reservations/${id}/cancel/`, { reason }),
  
  checkAvailability: (data: any) => api.post('/reservations/check-availability/', data),
  calculatePrice: (data: any) => api.post('/reservations/calculate-price/', data),
};

// Guests API
export const guestsApi = {
  list: (params?: any) => api.get('/guests/', { params }),
  get: (id: number) => api.get(`/guests/${id}/`),
  create: (data: any) => api.post('/guests/', data),
  update: (id: number, data: any) => api.patch(`/guests/${id}/`, data),
  search: (query: string) => api.get('/guests/', { params: { search: query } }),
};

// Front Desk API
export const frontdeskApi = {
  checkIn: (reservationId: number, data: any) => 
    api.post(`/frontdesk/check-in/${reservationId}/`, data),
  checkOut: (reservationId: number, data: any) => 
    api.post(`/frontdesk/check-out/${reservationId}/`, data),
  arrivals: (date?: string) => 
    api.get('/frontdesk/arrivals/', { params: { date } }),
  departures: (date?: string) => 
    api.get('/frontdesk/departures/', { params: { date } }),
  inHouse: () => api.get('/frontdesk/in-house/'),
};

// Housekeeping API
export const housekeepingApi = {
  tasks: {
    list: (params?: any) => api.get('/housekeeping/tasks/', { params }),
    get: (id: number) => api.get(`/housekeeping/tasks/${id}/`),
    create: (data: any) => api.post('/housekeeping/tasks/', data),
    update: (id: number, data: any) => api.patch(`/housekeeping/tasks/${id}/`, data),
    complete: (id: number) => api.post(`/housekeeping/tasks/${id}/complete/`),
  },
  
  rooms: {
    list: (status?: string) => 
      api.get('/housekeeping/rooms/', { params: { status } }),
    updateStatus: (roomId: number, status: string) => 
      api.post(`/housekeeping/rooms/${roomId}/status/`, { status }),
  },
};

// Maintenance API
export const maintenanceApi = {
  list: (params?: any) => api.get('/maintenance/', { params }),
  get: (id: number) => api.get(`/maintenance/${id}/`),
  create: (data: any) => api.post('/maintenance/', data),
  update: (id: number, data: any) => api.patch(`/maintenance/${id}/`, data),
  resolve: (id: number, notes: string) => 
    api.post(`/maintenance/${id}/resolve/`, { notes }),
};

// Billing API
export const billingApi = {
  invoices: {
    list: (params?: any) => api.get('/billing/invoices/', { params }),
    get: (id: number) => api.get(`/billing/invoices/${id}/`),
    create: (data: any) => api.post('/billing/invoices/', data),
    pay: (id: number, data: any) => api.post(`/billing/invoices/${id}/pay/`, data),
  },
  
  payments: {
    list: (params?: any) => api.get('/billing/payments/', { params }),
    get: (id: number) => api.get(`/billing/payments/${id}/`),
  },
  
  folios: {
    get: (reservationId: number) => api.get(`/billing/folios/${reservationId}/`),
    addCharge: (reservationId: number, data: any) => 
      api.post(`/billing/folios/${reservationId}/charges/`, data),
  },
  
  // Additional methods for new screens
  getInvoiceDetail: (id: number) => api.get(`/billing/invoices/${id}/`),
  recordPayment: (id: number, data: any) => api.post(`/billing/invoices/${id}/pay/`, data),
};

// POS API
export const posApi = {
  outlets: {
    list: () => api.get('/pos/outlets/'),
    get: (id: number) => api.get(`/pos/outlets/${id}/`),
  },
  
  menu: {
    get: (outletId: number) => api.get(`/pos/outlets/${outletId}/menu/`),
  },
  
  orders: {
    list: (params?: any) => api.get('/pos/orders/', { params }),
    get: (id: number) => api.get(`/pos/orders/${id}/`),
    create: (data: any) => api.post('/pos/orders/create/', data),
    addItem: (id: number, data: any) => api.post(`/pos/orders/${id}/add-item/`, data),
    postToRoom: (id: number, data: any) => api.post(`/pos/orders/${id}/post-to-room/`, data),
  },
  
  // Additional methods for new screens
  listOrders: (params?: any) => api.get('/pos/orders/', { params }),
  getOrderDetail: (id: number) => api.get(`/pos/orders/${id}/`),
};

// Rates API
export const ratesApi = {
  plans: {
    list: () => api.get('/rates/plans/'),
    get: (id: number) => api.get(`/rates/plans/${id}/`),
  },
  
  seasons: {
    list: () => api.get('/rates/seasons/'),
  },
  
  roomRates: {
    list: (params?: any) => api.get('/rates/room-rates/', { params }),
  },
};

// Channels API
export const channelsApi = {
  list: () => api.get('/channels/'),
  get: (id: number) => api.get(`/channels/${id}/`),
  
  propertyChannels: {
    list: () => api.get('/channels/property-channels/'),
  },
  
  roomMappings: {
    list: () => api.get('/channels/room-mappings/'),
  },
};

// Notifications API
export const notificationsApi = {
  list: () => api.get('/notifications/'),
  unread: () => api.get('/notifications/unread/'),
  get: (id: number) => api.get(`/notifications/${id}/`),
  markRead: (id: number) => api.post(`/notifications/${id}/read/`),
};

// Reports API
export const reportsApi = {
  dashboard: () => api.get('/reports/dashboard/'),
  occupancy: (params: any) => api.get('/reports/occupancy/', { params }),
  revenue: (params: any) => api.get('/reports/revenue/', { params }),
  dailyStats: (date: string) => api.get('/reports/daily/', { params: { date } }),
};

// Export all
export default {
  properties: propertiesApi,
  rooms: roomsApi,
  reservations: reservationsApi,
  guests: guestsApi,
  frontdesk: frontdeskApi,
  housekeeping: housekeepingApi,
  maintenance: maintenanceApi,
  billing: billingApi,
  pos: posApi,
  rates: ratesApi,
  channels: channelsApi,
  notifications: notificationsApi,
  reports: reportsApi,
};
