import api from './api';

// Properties API
export const propertiesApi = {
  list: () => api.get('/properties/'),
  get: (id: number) => api.get(`/properties/${id}/`),
  create: (data: any) => api.post('/properties/', data),
  update: (id: number, data: any) => api.patch(`/properties/${id}/`, data),
  delete: (id: number) => api.delete(`/properties/${id}/`),
  
  // Companies
  companies: {
    list: () => api.get('/properties/companies/'),
    get: (id: number) => api.get(`/properties/companies/${id}/`),
    create: (data: any) => api.post('/properties/companies/', data),
    update: (id: number, data: any) => api.patch(`/properties/companies/${id}/`, data),
    delete: (id: number) => api.delete(`/properties/companies/${id}/`),
  },
  
  // Buildings
  buildings: {
    list: (params?: any) => api.get('/properties/buildings/', { params }),
    get: (id: number) => api.get(`/properties/buildings/${id}/`),
    create: (data: any) => api.post('/properties/buildings/', data),
    update: (id: number, data: any) => api.patch(`/properties/buildings/${id}/`, data),
    delete: (id: number) => api.delete(`/properties/buildings/${id}/`),
  },
  
  // Floors
  floors: {
    list: (params?: any) => api.get('/properties/floors/', { params }),
    get: (id: number) => api.get(`/properties/floors/${id}/`),
    create: (data: any) => api.post('/properties/floors/', data),
    update: (id: number, data: any) => api.patch(`/properties/floors/${id}/`, data),
    delete: (id: number) => api.delete(`/properties/floors/${id}/`),
  },
};

// Rooms API
export const roomsApi = {
  list: (params?: any) => api.get('/rooms/', { params }),
  get: (id: number) => api.get(`/rooms/${id}/`),
  create: (data: any) => api.post('/rooms/', data),
  update: (id: number, data: any) => api.patch(`/rooms/${id}/`, data),
  delete: (id: number) => api.delete(`/rooms/${id}/`),
  getAvailable: (params: any) => api.get('/rooms/available/', { params }),
  updateStatus: (id: number, status: string) => api.post(`/rooms/${id}/status/`, { status }),
  
  // Room Types
  types: {
    list: () => api.get('/rooms/types/'),
    get: (id: number) => api.get(`/rooms/types/${id}/`),
    create: (data: any) => api.post('/rooms/types/', data),
    update: (id: number, data: any) => api.patch(`/rooms/types/${id}/`, data),
    delete: (id: number) => api.delete(`/rooms/types/${id}/`),
  },
  
  // Room Amenities
  amenities: {
    list: () => api.get('/rooms/amenities/'),
    get: (id: number) => api.get(`/rooms/amenities/${id}/`),
    create: (data: any) => api.post('/rooms/amenities/', data),
    update: (id: number, data: any) => api.patch(`/rooms/amenities/${id}/`, data),
    delete: (id: number) => api.delete(`/rooms/amenities/${id}/`),
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
  dashboard: () => api.get('/frontdesk/dashboard/'),
  
  checkIn: (data: any) => api.post('/frontdesk/check-in/', data),
  checkOut: (data: any) => api.post('/frontdesk/check-out/', data),
  
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
    create: (data: any) => api.post('/billing/payments/', data),
  },
  
  folios: {
    list: (params?: any) => api.get('/billing/folios/', { params }),
    get: (id: number) => api.get(`/billing/folios/${id}/`),
    create: (data: any) => api.post('/billing/folios/', data),
    close: (id: number) => api.post(`/billing/folios/${id}/close/`),
    addCharge: (folioId: number, data: any) => 
      api.post(`/billing/folios/${folioId}/charges/`, data),
  },
  
  chargeCodes: {
    list: (params?: any) => api.get('/billing/charge-codes/', { params }),
    get: (id: number) => api.get(`/billing/charge-codes/${id}/`),
    create: (data: any) => api.post('/billing/charge-codes/', data),
    update: (id: number, data: any) => api.patch(`/billing/charge-codes/${id}/`, data),
    delete: (id: number) => api.delete(`/billing/charge-codes/${id}/`),
  },
  
  // Additional methods for new screens
  getInvoiceDetail: (id: number) => api.get(`/billing/invoices/${id}/`),
  recordPayment: (invoiceId: number, data: any) => api.post(`/billing/invoices/${invoiceId}/pay/`, data),
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
    create: (data: any) => api.post('/rates/plans/', data),
    update: (id: number, data: any) => api.patch(`/rates/plans/${id}/`, data),
    delete: (id: number) => api.delete(`/rates/plans/${id}/`),
  },
  
  seasons: {
    list: () => api.get('/rates/seasons/'),
    get: (id: number) => api.get(`/rates/seasons/${id}/`),
    create: (data: any) => api.post('/rates/seasons/', data),
    update: (id: number, data: any) => api.patch(`/rates/seasons/${id}/`, data),
    delete: (id: number) => api.delete(`/rates/seasons/${id}/`),
  },
  
  roomRates: {
    list: (params?: any) => api.get('/rates/room-rates/', { params }),
    get: (id: number) => api.get(`/rates/room-rates/${id}/`),
    create: (data: any) => api.post('/rates/room-rates/', data),
    update: (id: number, data: any) => api.patch(`/rates/room-rates/${id}/`, data),
    delete: (id: number) => api.delete(`/rates/room-rates/${id}/`),
  },
  
  dateRates: {
    list: (params?: any) => api.get('/rates/date-rates/', { params }),
    get: (id: number) => api.get(`/rates/date-rates/${id}/`),
    create: (data: any) => api.post('/rates/date-rates/', data),
    update: (id: number, data: any) => api.patch(`/rates/date-rates/${id}/`, data),
    delete: (id: number) => api.delete(`/rates/date-rates/${id}/`),
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
