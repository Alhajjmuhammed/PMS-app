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
  room_number: string;
  status: string;
  room_type?: number;
  room_type_name?: string;
  room_type_detail?: {
    id: number;
    name: string;
    base_rate: number;
    max_occupancy?: number;
    bed_type?: string;
  };
  floor_name?: string;
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
    const response = await api.post('/api/v1/reservations/create/', data);
    return response.data;
  },

  async update(id: number, data: any) {
    const response = await api.patch(`/api/v1/reservations/${id}/`, data);
    return response.data;
  },

  async delete(id: number) {
    await api.delete(`/api/v1/reservations/${id}/`);
  },

  async cancel(id: number, reason?: string) {
    const response = await api.post(`/api/v1/reservations/${id}/cancel/`, { reason: reason ?? '' });
    return response.data;
  },

  async checkIn(reservationId: number, roomId: number) {
    const response = await api.post('/api/v1/frontdesk/check-in/', {
      reservation_id: reservationId,
      room_id: roomId,
    });
    return response.data;
  },

  async checkOut(id: number) {
    const response = await api.post(`/api/v1/reservations/${id}/checkout/`);
    return response.data;
  },

  async confirm(id: number) {
    const response = await api.post(`/api/v1/reservations/${id}/confirm/`);
    return response.data;
  },

  async noShow(id: number) {
    const response = await api.post(`/api/v1/reservations/${id}/no-show/`);
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

  async create(data: any) {
    const response = await api.post('/api/v1/rooms/create/', data);
    return response.data;
  },

  async update(id: number, data: any) {
    const response = await api.patch(`/api/v1/rooms/${id}/`, data);
    return response.data;
  },

  async delete(id: number) {
    await api.delete(`/api/v1/rooms/${id}/`);
  },

  async updateStatus(id: number, status: string) {
    const response = await api.post(`/api/v1/rooms/${id}/status/`, { status });
    return response.data;
  },
};

export const floorService = {
  async getAll(params?: any) {
    const response = await api.get('/api/v1/properties/floors/', { params });
    return response.data;
  },
};

export const roomTypeService = {
  async getAll(params?: any) {
    const response = await api.get('/api/v1/rooms/types/', { params });
    return response.data;
  },

  async getActive() {
    const response = await api.get('/api/v1/rooms/types/active/');
    return response.data;
  },

  async getById(id: number) {
    const response = await api.get(`/api/v1/rooms/types/${id}/`);
    return response.data;
  },

  async create(data: any) {
    const response = await api.post('/api/v1/rooms/types/', data);
    return response.data;
  },

  async update(id: number, data: any) {
    const response = await api.patch(`/api/v1/rooms/types/${id}/`, data);
    return response.data;
  },

  async delete(id: number) {
    await api.delete(`/api/v1/rooms/types/${id}/`);
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

  async delete(id: number) {
    await api.delete(`/api/v1/guests/${id}/`);
  },
};
