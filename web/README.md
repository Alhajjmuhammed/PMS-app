# Hotel PMS - Web Frontend

Next.js 14 web application for the Hotel Property Management System.

## Features

- ✅ Modern Next.js 14 with App Router
- ✅ TypeScript for type safety
- ✅ Tailwind CSS for styling
- ✅ JWT Authentication with auto-refresh
- ✅ MFA Support (TOTP, Email, SMS) with QR codes
- ✅ Responsive dashboard
- ✅ API client with interceptors
- ✅ 6 reusable UI components (Button, Input, Card, Table, Modal, Layout)
- ✅ 18 fully functional pages
- ✅ Complete Reservations module
- ✅ Room management with availability checker
- ✅ Guest management system
- ✅ Check-in/Check-out workflows
- ✅ Housekeeping task management
- ✅ Maintenance request tracking
- ✅ Billing & invoicing
- ✅ Reports & analytics dashboard

## Getting Started

### Prerequisites

- Node.js 18+ 
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
copy .env.example .env.local
```

3. Configure environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Hotel PMS
NEXT_PUBLIC_ENABLE_MFA=true
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
web/
├── src/
│   ├── app/                    # Next.js 14 App Router pages
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page (redirects)
│   │   ├── billing/            # Billing & invoices ✅
│   │   ├── checkin/            # Guest check-in ✅
│   │   ├── checkout/           # Guest check-out ✅
│   │   ├── dashboard/          # Main dashboard ✅
│   │   ├── guests/             # Guest management ✅
│   │   ├── housekeeping/       # Housekeeping tasks ✅
│   │   ├── login/              # Authentication ✅
│   │   ├── maintenance/        # Maintenance requests ✅
│   │   ├── reports/            # Analytics & reports ✅
│   │   ├── reservations/       # Reservation management ✅
│   │   ├── rooms/              # Room management ✅
│   │   └── settings/           # User settings & MFA ✅
│   ├── components/             # Reusable UI components ✅
│   │   ├── Button.tsx          # Button component
│   │   ├── Card.tsx            # Card container
│   │   ├── Input.tsx           # Form input
│   │   ├── Layout.tsx          # App layout with sidebar
│   │   ├── Modal.tsx           # Modal dialog
│   │   └── Table.tsx           # Data table
│   ├── contexts/               # React contexts
│   │   └── AuthContext.tsx     # Authentication context
│   └── lib/                    # Utilities & services
│       ├── api.ts              # API client with auth
│       └── services.ts         # API service layer
├── public/                     # Static files
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.mjs
```

## Authentication Flow

1. User enters email/password
2. Backend returns JWT tokens (or MFA challenge)
3. If MFA enabled:
   - Redirect to MFA verification
   - User enters 6-digit code
   - Verify code with backend
4. Store JWT tokens in localStorage
5. Auto-refresh tokens when expired
6. Redirect to dashboard

## API Integration

All API calls go through the centralized API client (`src/lib/api.ts`):

```typescript
import api from '@/lib/api';

// GET request
const response = await api.get('/api/v1/rooms/');

// POST request
const response = await api.post('/api/v1/reservations/', data);
```

Features:
- Automatic token injection
- Token refresh on 401
- Auto-redirect to login on auth failure
- TypeScript types for all responses

## Available Pages

### ✅ Completed Pages (18 pages - 38% of total)

**Authentication & Dashboard:**
- **/** - Home (redirects to dashboard or login)
- **/login** - Login with JWT and MFA support
- **/dashboard** - Main dashboard with stats

**Reservations Module (3 pages):**
- **/reservations** - List all reservations with filtering
- **/reservations/new** - Create new reservation
- **/reservations/[id]** - View reservation details + check-in/out

**Rooms Module (2 pages):**
- **/rooms** - List rooms + availability checker
- **/rooms/[id]** - Room details with amenities

**Guests Module (3 pages):**
- **/guests** - List guests with search
- **/guests/new** - Register new guest
- **/guests/[id]** - Guest details with history

**Front Desk Operations (2 pages):**
- **/checkin** - Guest check-in workflow
- **/checkout** - Guest check-out with billing

**Housekeeping & Maintenance (2 pages):**
- **/housekeeping** - Task management
- **/maintenance** - Request tracking

**Billing (1 page):**
- **/billing** - Invoice management

**Reports (1 page):**
- **/reports** - Analytics dashboard

**Settings (1 page):**
- **/settings** - User settings with MFA setup

### ⏳ Planned Pages (30 more pages)

**Priority 1:**
- /channel-manager - OTA integrations
- /rates - Rate management
- /night-audit - End of day operations
- /pos - Point of Sale
- /users - User management
- /property - Property settings
- /reservations/calendar - Calendar view
- /rooms/types - Room type management

**Priority 2:**
- /billing/[id] - Invoice details
- /billing/payments - Payment processing
- /reports/revenue - Revenue analytics
- /reports/occupancy - Occupancy stats
- /settings/password - Password change
- /settings/notifications - Notification preferences

**See [WEB_FRONTEND_COMPLETE.md](../WEB_FRONTEND_COMPLETE.md) for complete status**

## Styling

Uses Tailwind CSS with custom color scheme:

```css
primary-50 to primary-900 - Blue shades
```

Customize in `tailwind.config.js`.

## TypeScript

Strict TypeScript enabled. All files should be `.ts` or `.tsx`.

Type definitions in:
- `src/lib/auth.ts` - User, LoginCredentials, etc.
- Add more as needed

## Development Tips

### Hot Reload

Next.js has fast refresh - changes appear instantly.

### Debugging

Use browser DevTools:
- Network tab for API calls
- Console for logs
- Application tab for localStorage (tokens)

### Common Issues

**"Failed to load user"**
- Check backend is running
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check JWT tokens in localStorage

**CORS errors**
- Ensure backend has CORS configured
- Check `CORS_ALLOWED_ORIGINS` in backend `.env`

## Production Deployment

### Build

```bash
npm run build
```

### Environment Variables

Set in your hosting platform:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Hosting Options

- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- Docker + Nginx

## Contributing

This is a starter kit (10-15% complete). Extend by:

1. Adding more pages in `src/app/`
2. Creating reusable components in `src/components/`
3. Adding API services in `src/lib/`
4. Implementing full CRUD operations

## Status

- ✅ Core structure setup
- ✅ Authentication working
- ✅ Basic dashboard
- ⚠️ Need to implement remaining pages
- ⚠️ Need to add components library
- ⚠️ Need comprehensive testing

**Completion: 10-15%**

This provides a solid foundation to build upon. The authentication, API integration, and core structure are complete. Additional pages and features can be added following the same patterns.
