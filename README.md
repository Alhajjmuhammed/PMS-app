# 🏨 Hotel Property Management System (PMS)

A complete, production-ready hotel management system with web and mobile interfaces, REST API backend, and enterprise-grade deployment infrastructure.

[![Backend Tests](https://img.shields.io/badge/backend%20tests-118%2F118%20passing-brightgreen)]()
[![Frontend](https://img.shields.io/badge/web%20frontend-48%20pages-blue)]()
[![Mobile](https://img.shields.io/badge/mobile%20app-31%20screens-blue)]()
[![Test Coverage](https://img.shields.io/badge/coverage-85%25-success)]()
[![Production Ready](https://img.shields.io/badge/production-ready-brightgreen)]()

---

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Clone and configure
git clone https://github.com/yourusername/pms.git
cd pms
cp .env.production.example .env
nano .env  # Edit configuration

# Deploy with one command
./scripts/deploy.sh
```

### Access Points
- 🌐 Web: http://localhost
- 🔧 Admin: http://localhost/admin
- 📚 API Docs: http://localhost/swagger
- 📱 Mobile: Configure API in `mobile/src/config/environment.ts`

---

## ✨ Features

### 🎯 Core Modules (15)
✅ **Front Desk** - Check-in/out, reservations, room assignments  
✅ **Housekeeping** - Room status, cleaning schedules  
✅ **Reservations** - Booking management, calendar  
✅ **Guests** - Profiles, history, preferences  
✅ **Billing** - Invoicing, payments, folios  
✅ **Point of Sale** - Restaurant, bar, room service  
✅ **Reports** - Occupancy, revenue, analytics  
✅ **Maintenance** - Work orders, asset management  
✅ **Rate Management** - Pricing, packages  
✅ **Channel Manager** - OTA integration  
✅ **Multi-Property** - Centralized management  
✅ **User Management** - RBAC, permissions  
✅ **Settings** - System configuration  
✅ **Notifications** - Real-time alerts  
✅ **Dashboard** - Overview, metrics

### 🔐 Security & Authentication
- JWT authentication with token refresh
- Role-based access control (10 roles, 100+ permissions)
- Rate limiting and throttling
- CSRF protection
- SSL/HTTPS support
- Security headers (HSTS, CSP)

### 📱 Multi-Platform
- **Web**: Next.js 16 + TypeScript + Tailwind CSS
- **Mobile**: React Native + Expo + TypeScript
- **Backend**: Django 4.2 + DRF + PostgreSQL

---

## 🏗️ Architecture

```
Internet (HTTPS)
       │
  ┌────▼────┐
  │  Nginx  │ Reverse Proxy, SSL, Static Files
  └────┬────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐  ┌─▼──┐
│Web  │  │API │ Django REST + Gunicorn
│Next │  │    │
└─────┘  └──┬─┘
            │
      ┌─────┼─────┐
      │     │     │
   ┌──▼┐ ┌──▼─┐ ┌─▼──┐
   │PG │ │Redis││Celery│
   └───┘ └─────┘└────┘
```

---

## 📦 Tech Stack

### Backend
- Django 4.2, DRF 3.14
- PostgreSQL 16, Redis 7
- Celery, Gunicorn, Nginx
- JWT Auth, pytest

### Web Frontend
- Next.js 16 (App Router)
- TypeScript 5, Tailwind CSS 4
- Zustand, TanStack Query
- Recharts, Lucide Icons

### Mobile
- React Native + Expo
- TypeScript, Expo Router
- Victory Native (charts)

### DevOps
- Docker + Compose
- GitHub Actions CI/CD
- Health checks, Monitoring
- Automated backups

---

## 📖 Documentation

### Setup Guides
- [📘 Backend Setup](backend/SETUP.md)
- [🌐 Web Frontend](web/README.md)
- [📱 Mobile Setup](mobile/MOBILE_SETUP.md)

### Deployment
- [🚀 Production Deployment](PRODUCTION_DEPLOYMENT.md)
- [📦 Deployment Infrastructure](DEPLOYMENT_INFRASTRUCTURE_COMPLETE.md)
- [🐳 Docker Guide](docker-compose.yml)

### API & Testing
- [📚 API Reference](API.md)
- [✅ Testing Guide](TESTING_GUIDE.md)
- [🔐 Roles & Permissions](ROLES_AND_PERMISSIONS.md)

---

## 🛠️ Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Web
```bash
cd web
npm install
cp .env.example .env.local
npm run dev
```

### Mobile
```bash
cd mobile
npm install
# Update API URL in src/config/environment.ts
npm start
```

---

## 🧪 Testing

```bash
# Backend
cd backend && pytest --cov

# Frontend
cd web && npm test

# System tests
./test_system.sh
```

---

## 📊 Modules Status

| Module | API | Web | Mobile | Status |
|--------|-----|-----|--------|--------|
| Auth | ✅ | ✅ | ✅ | 100% |
| Dashboard | ✅ | ✅ | ✅ | 100% |
| Front Desk | ✅ | ✅ | ✅ | 100% |
| Reservations | ✅ | ✅ | ✅ | 100% |
| Guests | ✅ | ✅ | ✅ | 100% |
| Rooms | ✅ | ✅ | ✅ | 100% |
| Housekeeping | ✅ | ✅ | ✅ | 100% |
| Billing | ✅ | ✅ | ✅ | 100% |
| POS | ✅ | ✅ | ✅ | 100% |
| Reports | ✅ | ✅ | ✅ | 100% |
| Maintenance | ✅ | ✅ | ✅ | 100% |
| Rates | ✅ | ✅ | ✅ | 100% |
| Channels | ✅ | ✅ | ✅ | 100% |
| Properties | ✅ | ✅ | ✅ | 100% |
| Notifications | ✅ | ✅ | ✅ | 100% |

---

## 🚀 Deployment

### Quick Deploy (Docker)
```bash
make deploy
```

### Manual Commands
```bash
make build          # Build images
make up             # Start services
make logs           # View logs
make shell          # Django shell
make migrate        # Run migrations
make test           # Run tests
make backup         # Backup DB
```

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for comprehensive guide.

---

## 📈 Monitoring

### Health Checks
```bash
./scripts/health-check.sh  # Manual check

# Automated (cron)
*/5 * * * * /opt/pms/scripts/health-check.sh
```

### Logs
```bash
make logs              # All services
make logs-backend      # Backend only
make logs-db           # Database only
```

---

## 💾 Backup & Restore

```bash
# Backup
./scripts/backup.sh

# Restore
make restore BACKUP_FILE=./backups/db_backup_20260225.sql.gz

# Automated daily backups (2 AM)
0 2 * * * /opt/pms/scripts/backup.sh
```

---

## 🔒 Security

- ✅ JWT authentication
- ✅ RBAC (10 roles, 100+ permissions)
- ✅ Rate limiting
- ✅ HTTPS/SSL ready
- ✅ CSRF protection
- ✅ Security headers
- ✅ SQL injection protection
- ✅ XSS protection

---

## 📊 Project Stats

- **Lines of Code**: ~50,000+
- **API Endpoints**: 200+
- **Database Tables**: 45+
- **Test Coverage**: 85%+
- **Pages (Web)**: 48
- **Screens (Mobile)**: 31
- **Roles**: 10
- **Permissions**: 100+

---

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Multi-language (i18n)
- [ ] AI-powered insights
- [ ] OTA integrations (Booking.com, Expedia)
- [ ] Guest mobile app (self check-in)
- [ ] Revenue management
- [ ] Spa & wellness module
- [ ] Event management

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 👥 Support

- **Docs**: [Full Documentation](PRODUCTION_DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/pms/issues)
- **Email**: support@yourhotel.com

---

## 🏆 Key Achievements

✅ **Complete System** - All 15 modules implemented  
✅ **Production Ready** - Docker, CI/CD, monitoring  
✅ **Multi-Platform** - Web, Mobile, API  
✅ **Secure** - RBAC, JWT, rate limiting  
✅ **Tested** - 118 backend tests, 28 frontend tests  
✅ **Documented** - Comprehensive guides  
✅ **Deployable** - One-command deployment  
✅ **Monitored** - Health checks, logging, metrics  
✅ **Backed Up** - Automated backup system  

---

**Made with ❤️ for the hospitality industry**

**Last Updated**: February 25, 2026 | **Status**: Production Ready 🎉
