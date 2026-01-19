// Type definitions for API responses and requests

// Common
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Property
export interface Property {
  id: number;
  name: string;
  code: string;
  address: string;
  city: string;
  country: string;
  phone: string;
  email: string;
  website?: string;
  total_rooms: number;
  is_active: boolean;
}

// Room
export interface RoomType {
  id: number;
  property: number;
  name: string;
  code: string;
  description?: string;
  max_occupancy: number;
  base_price: number;
  size_sqm?: number;
  bed_type?: string;
}

export interface Room {
  id: number;
  property: number;
  room_type: number;
  room_type_name: string;
  room_number: string;
  floor: number;
  status: 'AVAILABLE' | 'OCCUPIED' | 'CLEANING' | 'MAINTENANCE' | 'OUT_OF_SERVICE';
  is_active: boolean;
}

// Reservation
export interface Reservation {
  id: number;
  property: number;
  guest: number;
  guest_name: string;
  room: number;
  room_number: string;
  check_in_date: string;
  check_out_date: string;
  adults: number;
  children: number;
  status: 'PENDING' | 'CONFIRMED' | 'CHECKED_IN' | 'CHECKED_OUT' | 'CANCELLED';
  total_amount: string;
  paid_amount: string;
  balance: string;
  special_requests?: string;
  created_at: string;
}

export interface ReservationCreate {
  property: number;
  guest: number;
  room: number;
  check_in_date: string;
  check_out_date: string;
  adults: number;
  children: number;
  special_requests?: string;
  rate_plan?: number;
}

// Guest
export interface Guest {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  nationality?: string;
  id_type?: string;
  id_number?: string;
  date_of_birth?: string;
  address?: string;
  city?: string;
  country?: string;
  is_vip: boolean;
  created_at: string;
}

export interface GuestCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  nationality?: string;
  id_type?: string;
  id_number?: string;
  date_of_birth?: string;
  address?: string;
  city?: string;
  country?: string;
}

// Housekeeping
export interface HousekeepingTask {
  id: number;
  room: number;
  room_number: string;
  task_type: 'CLEANING' | 'INSPECTION' | 'TURNDOWN' | 'DEEP_CLEAN' | 'MAINTENANCE';
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  assigned_to?: number;
  assigned_to_name?: string;
  notes?: string;
  scheduled_time?: string;
  completed_at?: string;
}

// Maintenance
export interface MaintenanceRequest {
  id: number;
  property: number;
  room?: number;
  room_number?: string;
  issue_type: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  status: 'REPORTED' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  description: string;
  reported_by: number;
  assigned_to?: number;
  resolved_at?: string;
  created_at: string;
}

// Billing
export interface Invoice {
  id: number;
  reservation: number;
  guest_name: string;
  invoice_number: string;
  issue_date: string;
  due_date: string;
  total_amount: string;
  paid_amount: string;
  balance: string;
  status: 'DRAFT' | 'ISSUED' | 'PAID' | 'OVERDUE' | 'CANCELLED';
}

export interface Payment {
  id: number;
  invoice: number;
  amount: string;
  payment_method: 'CASH' | 'CARD' | 'BANK_TRANSFER' | 'MOBILE_MONEY' | 'OTHER';
  payment_date: string;
  reference_number?: string;
  notes?: string;
}

// POS
export interface Product {
  id: number;
  name: string;
  code: string;
  category: number;
  category_name: string;
  price: string;
  stock_quantity: number;
  is_active: boolean;
}

export interface Order {
  id: number;
  order_number: string;
  property: number;
  room?: number;
  guest?: number;
  items: OrderItem[];
  subtotal: string;
  tax: string;
  total: string;
  status: 'PENDING' | 'CONFIRMED' | 'DELIVERED' | 'CANCELLED';
  created_at: string;
}

export interface OrderItem {
  product: number;
  product_name: string;
  quantity: number;
  unit_price: string;
  total: string;
}

// Rates
export interface RatePlan {
  id: number;
  property: number;
  name: string;
  code: string;
  rate_type: 'STANDARD' | 'SEASONAL' | 'PACKAGE' | 'PROMOTIONAL';
  description?: string;
  min_nights?: number;
  max_nights?: number;
  is_refundable: boolean;
  is_active: boolean;
}

export interface Season {
  id: number;
  property: number;
  name: string;
  start_date: string;
  end_date: string;
  priority: number;
  is_active: boolean;
}

export interface RoomRate {
  id: number;
  rate_plan: number;
  room_type: number;
  season?: number;
  single_rate: string;
  double_rate: string;
  extra_adult: string;
  extra_child: string;
}

// Notifications
export interface Notification {
  id: number;
  user: number;
  notification_type: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

// Reports
export interface DashboardStats {
  total_rooms: number;
  occupied_rooms: number;
  available_rooms: number;
  occupancy_rate: number;
  arrivals_today: number;
  departures_today: number;
  total_revenue_today: string;
  total_revenue_month: string;
}

export interface OccupancyData {
  date: string;
  total_rooms: number;
  occupied_rooms: number;
  occupancy_rate: number;
}

export interface RevenueData {
  date: string;
  room_revenue: string;
  pos_revenue: string;
  total_revenue: string;
}

// API Error
export interface ApiError {
  message: string;
  statusCode?: number;
  details?: any;
}
