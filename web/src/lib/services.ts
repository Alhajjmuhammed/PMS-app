import api from './api';

export interface Reservation {
  id: number;
  guest: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  room: {
    id: number;
    number: string;
    type: {
      name: string;
    };
  };
  check_in: string;
  check_out: string;
  status: string;
  total_amount: number;
  adults: number;
  children: number;
  special_requests?: string;
}

export interface Room {
  id: number;
  number: string;
  floor: number;
  status: string;
  room_type: {
    id: number;
    name: string;
    base_price: number;
  };
  is_clean: boolean;
}

export interface Guest {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  id_type?: string;
  id_number?: string;
  nationality?: string;
  total_reservations?: number;
}

export const reservationService = {
  async getAll(params?: any) {
    const response = await api.get('/api/v1/reservations/', { params });
    return response.data;
  },

  async getById(id: number) {
    const response = await api.get(`/api/v1/reservations/${id}/`);
    return response.data;
  },

  async create(data: any) {
    const response = await api.post('/api/v1/reservations/', data);
    return response.data;
  },

  async update(id: number, data: any) {
    const response = await api.patch(`/api/v1/reservations/${id}/`, data);
    return response.data;
  },

  async delete(id: number) {
    await api.delete(`/api/v1/reservations/${id}/`);
  },

  async checkIn(id: number) {
    const response = await api.post(`/api/v1/reservations/${id}/checkin/`);
    return response.data;
  },

  async checkOut(id: number) {
    const response = await api.post(`/api/v1/reservations/${id}/checkout/`);
    return response.data;
  },
};

export const roomService = {
  async getAll(params?: any) {
    const response = await api.get('/api/v1/rooms/', { params });
    return response.data;
  },

  async getAvailability(check_in: string, check_out: string) {
    const response = await api.get('/api/v1/rooms/availability/', {
      params: { check_in, check_out },
    });
    return response.data;
  },

  async getById(id: number) {
    const response = await api.get(`/api/v1/rooms/${id}/`);
    return response.data;
  },
};

export const guestService = {
  async getAll(params?: any) {
    const response = await api.get('/api/v1/guests/', { params });
    return response.data;
  },

  async getById(id: number) {
    const response = await api.get(`/api/v1/guests/${id}/`);
    return response.data;
  },

  async create(data: any) {
    const response = await api.post('/api/v1/guests/', data);
    return response.data;
  },

  async update(id: number, data: any) {
    const response = await api.patch(`/api/v1/guests/${id}/`, data);
    return response.data;
  },
};
