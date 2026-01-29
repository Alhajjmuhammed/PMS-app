# Hotel PMS API Documentation

**Version:** 1.0.0  
**Base URL:** `http://your-domain.com/api/v1/`  
**Authentication:** Token-based authentication  

---

## Table of Contents

1. [Authentication](#authentication)
2. [Properties](#properties)
3. [Rooms](#rooms)
4. [Guests](#guests)
5. [Reservations](#reservations)
6. [Front Desk](#front-desk)
7. [Housekeeping](#housekeeping)
8. [Maintenance](#maintenance)
9. [Billing](#billing)
10. [POS](#pos)
11. [Reports](#reports)
12. [Rate Plans](#rate-plans)
13. [Channels](#channels)
14. [Notifications](#notifications)

---

## Authentication

### Login
```http
POST /api/v1/auth/login/
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "abc123xyz789...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "assigned_property": 1
  }
}
```

**Headers Required for All Authenticated Requests:**
```
Authorization: Token abc123xyz789...
```

### Register
```http
POST /api/v1/auth/register/
```

### Logout
```http
POST /api/v1/auth/logout/
```

### Change Password
```http
POST /api/v1/auth/change-password/
```

---

## Properties

### List Properties
```http
GET /api/v1/properties/
```

**Permissions:** Authenticated users  
**Returns:** List of properties accessible to the user

**Response:**
```json
[
  {
    "id": 1,
    "name": "Grand Hotel",
    "code": "GH001",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "phone": "+1234567890",
    "email": "info@grandhotel.com",
    "website": "https://grandhotel.com",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

### Create Property
```http
POST /api/v1/properties/
```

**Permissions:** Admin or Manager  
**Request Body:** Same as response above (without id, created_at)

### Get Property Details
```http
GET /api/v1/properties/{id}/
```

### Update Property
```http
PUT /api/v1/properties/{id}/
PATCH /api/v1/properties/{id}/
```

### Delete Property
```http
DELETE /api/v1/properties/{id}/
```

---

## Rooms

### List Rooms
```http
GET /api/v1/rooms/
```

**Query Parameters:**
- `status` - Filter by status (AVAILABLE, OCCUPIED, DIRTY, CLEAN, MAINTENANCE, OUT_OF_ORDER)
- `room_type` - Filter by room type ID
- `floor` - Filter by floor number
- `search` - Search by room number or room type name
- `ordering` - Order by field (room_number, floor, status)

**Response:**
```json
[
  {
    "id": 1,
    "room_number": "101",
    "room_type": {
      "id": 1,
      "name": "Deluxe Room",
      "description": "Spacious room with city view",
      "base_occupancy": 2,
      "max_occupancy": 4
    },
    "floor": 1,
    "status": "AVAILABLE",
    "is_smoking": false,
    "is_accessible": true,
    "view_type": "CITY",
    "is_active": true
  }
]
```

### Create Room
```http
POST /api/v1/rooms/create/
```

**Permissions:** Admin or Manager  

**Request Body:**
```json
{
  "room_number": "102",
  "room_type": 1,
  "floor": 1,
  "status": "AVAILABLE",
  "is_smoking": false,
  "is_accessible": false,
  "view_type": "GARDEN"
}
```

### Get Room Details
```http
GET /api/v1/rooms/{id}/
```

### Update Room
```http
PUT /api/v1/rooms/{id}/
PATCH /api/v1/rooms/{id}/
```

### Delete Room
```http
DELETE /api/v1/rooms/{id}/
```

### Check Room Availability
```http
GET /api/v1/rooms/availability/
```

**Query Parameters:**
- `check_in` - Check-in date (YYYY-MM-DD)
- `check_out` - Check-out date (YYYY-MM-DD)
- `room_type` - Room type ID (optional)
- `guests` - Number of guests (optional)

### Get Room Status History
```http
GET /api/v1/rooms/{id}/status-history/
```

---

## Guests

### List Guests
```http
GET /api/v1/guests/
```

**Query Parameters:**
- `search` - Search by name, email, or phone
- `ordering` - Order by field
- `is_vip` - Filter VIP guests

**Response:**
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "date_of_birth": "1985-05-15",
    "nationality": "USA",
    "passport_number": "AB123456",
    "is_vip": false,
    "loyalty_tier": "GOLD",
    "total_stays": 5,
    "preferences": {
      "room_type": "Deluxe",
      "floor_preference": "high",
      "pillow_type": "soft"
    }
  }
]
```

### Create Guest
```http
POST /api/v1/guests/
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1234567891",
  "date_of_birth": "1990-03-20",
  "nationality": "USA",
  "passport_number": "CD789012",
  "address": "456 Oak Ave",
  "city": "Boston",
  "state": "MA",
  "country": "USA",
  "postal_code": "02101"
}
```

### Get Guest Details
```http
GET /api/v1/guests/{id}/
```

### Update Guest
```http
PUT /api/v1/guests/{id}/
PATCH /api/v1/guests/{id}/
```

### Get Guest Reservation History
```http
GET /api/v1/guests/{id}/reservations/
```

---

## Reservations

### List Reservations
```http
GET /api/v1/reservations/
```

**Query Parameters:**
- `status` - Filter by status (PENDING, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED, NO_SHOW)
- `check_in` - Filter by check-in date
- `check_out` - Filter by check-out date
- `guest` - Filter by guest ID
- `room` - Filter by room ID

**Response:**
```json
[
  {
    "id": 1,
    "confirmation_number": "RES-2026-001",
    "guest": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com"
    },
    "rooms": [
      {
        "id": 1,
        "room_number": "101",
        "room_type": "Deluxe Room"
      }
    ],
    "check_in": "2026-02-01",
    "check_out": "2026-02-05",
    "adults": 2,
    "children": 0,
    "status": "CONFIRMED",
    "total_amount": 800.00,
    "paid_amount": 200.00,
    "balance": 600.00,
    "special_requests": "Late check-in",
    "created_at": "2026-01-23T10:00:00Z"
  }
]
```

### Create Reservation
```http
POST /api/v1/reservations/
```

**Request Body:**
```json
{
  "guest": 1,
  "room_type": 1,
  "check_in": "2026-02-10",
  "check_out": "2026-02-15",
  "adults": 2,
  "children": 1,
  "special_requests": "High floor preferred",
  "rate_plan": 1
}
```

### Get Reservation Details
```http
GET /api/v1/reservations/{id}/
```

### Update Reservation
```http
PUT /api/v1/reservations/{id}/
PATCH /api/v1/reservations/{id}/
```

### Cancel Reservation
```http
POST /api/v1/reservations/{id}/cancel/
```

---

## Front Desk

### Check In
```http
POST /api/v1/frontdesk/checkin/
```

**Request Body:**
```json
{
  "reservation": 1,
  "room": 101,
  "actual_arrival_time": "2026-02-01T15:30:00Z",
  "id_verified": true,
  "deposit_collected": 100.00,
  "notes": "Early check-in approved"
}
```

### Check Out
```http
POST /api/v1/frontdesk/checkout/
```

**Request Body:**
```json
{
  "reservation": 1,
  "actual_departure_time": "2026-02-05T11:00:00Z",
  "room_condition": "CLEAN",
  "minibar_charges": 25.00,
  "damage_charges": 0.00
}
```

### Walk-In Guest
```http
POST /api/v1/frontdesk/walkin/
```

### Room Move
```http
POST /api/v1/frontdesk/room-move/
```

---

## Housekeeping

### List Housekeeping Tasks
```http
GET /api/v1/housekeeping/tasks/
```

**Query Parameters:**
- `status` - Filter by status (PENDING, IN_PROGRESS, COMPLETED, VERIFIED)
- `assigned_to` - Filter by staff member ID
- `priority` - Filter by priority (LOW, MEDIUM, HIGH, URGENT)
- `date` - Filter by date

**Response:**
```json
[
  {
    "id": 1,
    "room": {
      "id": 1,
      "room_number": "101"
    },
    "task_type": "CLEANING",
    "priority": "HIGH",
    "status": "PENDING",
    "assigned_to": {
      "id": 5,
      "username": "housekeeper1",
      "first_name": "Maria",
      "last_name": "Garcia"
    },
    "scheduled_time": "2026-01-23T09:00:00Z",
    "notes": "Deep cleaning required",
    "created_at": "2026-01-23T08:00:00Z"
  }
]
```

### Create Housekeeping Task
```http
POST /api/v1/housekeeping/tasks/
```

### Update Task Status
```http
PATCH /api/v1/housekeeping/tasks/{id}/
```

### Room Inspection
```http
POST /api/v1/housekeeping/inspection/
```

---

## Maintenance

### List Maintenance Requests
```http
GET /api/v1/maintenance/requests/
```

**Query Parameters:**
- `status` - Filter by status (PENDING, IN_PROGRESS, COMPLETED, CANCELLED)
- `priority` - Filter by priority
- `assigned_to` - Filter by technician ID

**Response:**
```json
[
  {
    "id": 1,
    "room": {
      "id": 1,
      "room_number": "101"
    },
    "issue_type": "ELECTRICAL",
    "priority": "HIGH",
    "status": "IN_PROGRESS",
    "description": "Light fixture not working",
    "reported_by": {
      "id": 2,
      "username": "frontdesk1"
    },
    "assigned_to": {
      "id": 8,
      "username": "technician1"
    },
    "created_at": "2026-01-23T07:30:00Z",
    "estimated_completion": "2026-01-23T12:00:00Z"
  }
]
```

### Create Maintenance Request
```http
POST /api/v1/maintenance/requests/
```

### Update Maintenance Request
```http
PATCH /api/v1/maintenance/requests/{id}/
```

---

## Billing

### List Folios
```http
GET /api/v1/billing/folios/
```

### Get Folio Details
```http
GET /api/v1/billing/folios/{id}/
```

### Add Charge to Folio
```http
POST /api/v1/billing/charges/
```

**Request Body:**
```json
{
  "folio": 1,
  "charge_code": "ROOM",
  "description": "Room charge",
  "amount": 200.00,
  "quantity": 1,
  "date": "2026-02-01"
}
```

### Record Payment
```http
POST /api/v1/billing/payments/
```

**Request Body:**
```json
{
  "folio": 1,
  "amount": 200.00,
  "payment_method": "CREDIT_CARD",
  "reference_number": "CC123456",
  "notes": "Visa ending in 1234"
}
```

### Generate Invoice
```http
GET /api/v1/billing/invoices/{folio_id}/generate/
```

**Response:** PDF file download

---

## POS

### List POS Orders
```http
GET /api/v1/pos/orders/
```

### Create POS Order
```http
POST /api/v1/pos/orders/
```

**Request Body:**
```json
{
  "outlet": 1,
  "table_number": "5",
  "items": [
    {
      "menu_item": 1,
      "quantity": 2,
      "special_instructions": "No onions"
    }
  ],
  "guest": 1,
  "charge_to_room": "101"
}
```

### Menu Items
```http
GET /api/v1/pos/menu-items/
```

---

## Reports

### Daily Statistics
```http
GET /api/v1/reports/daily-statistics/
```

**Query Parameters:**
- `date` - Date for report (YYYY-MM-DD)
- `property` - Property ID

**Response:**
```json
{
  "date": "2026-01-23",
  "occupancy_rate": 85.5,
  "total_rooms": 100,
  "occupied_rooms": 86,
  "available_rooms": 14,
  "revenue": {
    "room_revenue": 17200.00,
    "food_beverage": 3500.00,
    "other": 800.00,
    "total": 21500.00
  },
  "arrivals": 12,
  "departures": 10,
  "current_guests": 142,
  "adr": 200.00,
  "revpar": 171.00
}
```

### Monthly Statistics
```http
GET /api/v1/reports/monthly-statistics/
```

### Revenue Report
```http
GET /api/v1/reports/revenue/
```

### Occupancy Report
```http
GET /api/v1/reports/occupancy/
```

---

## Rate Plans

### List Rate Plans
```http
GET /api/v1/rates/plans/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Best Available Rate",
    "code": "BAR",
    "description": "Standard rack rate",
    "is_active": true,
    "min_stay": 1,
    "max_stay": 30,
    "advance_booking_days": 0,
    "cancellation_policy": "Free cancellation up to 24 hours before check-in",
    "room_rates": [
      {
        "room_type": 1,
        "rate": 200.00
      }
    ]
  }
]
```

### Create Rate Plan
```http
POST /api/v1/rates/plans/
```

### Update Rate Plan
```http
PUT /api/v1/rates/plans/{id}/
PATCH /api/v1/rates/plans/{id}/
```

### Delete Rate Plan
```http
DELETE /api/v1/rates/plans/{id}/
```

### List Seasons
```http
GET /api/v1/rates/seasons/
```

---

## Channels

### List Channel Connections
```http
GET /api/v1/channels/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Booking.com",
    "code": "BOOKING",
    "is_active": true,
    "api_key": "***hidden***",
    "property_mappings": [
      {
        "property": 1,
        "channel_property_id": "12345"
      }
    ],
    "last_sync": "2026-01-23T10:00:00Z"
  }
]
```

### Create Channel Connection
```http
POST /api/v1/channels/
```

### Update Channel
```http
PUT /api/v1/channels/{id}/
PATCH /api/v1/channels/{id}/
```

### Delete Channel
```http
DELETE /api/v1/channels/{id}/
```

### Sync Availability
```http
POST /api/v1/channels/{id}/sync-availability/
```

### Sync Rates
```http
POST /api/v1/channels/{id}/sync-rates/
```

---

## Notifications

### List Notifications
```http
GET /api/v1/notifications/
```

### Mark as Read
```http
POST /api/v1/notifications/{id}/mark-read/
```

### Send Push Notification
```http
POST /api/v1/notifications/push/
```

---

## Error Responses

All endpoints return standard error responses:

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

- **Anonymous users:** 100 requests/hour
- **Authenticated users:** 1000 requests/hour

Headers returned:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643040000
```

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Response:**
```json
{
  "count": 150,
  "next": "http://api.example.com/api/v1/rooms/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Filtering and Search

Most list endpoints support:
- **Filtering:** `?field=value`
- **Search:** `?search=query`
- **Ordering:** `?ordering=field` or `?ordering=-field` (descending)

---

## Webhooks (Coming Soon)

Webhook support for real-time notifications of:
- New reservations
- Check-ins/Check-outs
- Payment received
- Maintenance requests

---

**Last Updated:** January 23, 2026  
**API Version:** 1.0.0  
**Support:** api-support@your-domain.com
