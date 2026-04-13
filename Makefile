# PMS - Makefile for common commands

.PHONY: help build up down restart logs shell migrate collectstatic test backup deploy clean

help:
	@echo "PMS - Available Commands:"
	@echo ""
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-backend   - View backend logs"
	@echo "  make logs-db        - View database logs"
	@echo "  make shell          - Open Django shell"
	@echo "  make bash           - Open bash in backend container"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make collectstatic  - Collect static files"
	@echo "  make createsuperuser- Create Django superuser"
	@echo "  make test           - Run tests"
	@echo "  make test-backend   - Run backend tests only"
	@echo "  make backup         - Backup database and media"
	@echo "  make restore        - Restore from backup"
	@echo "  make deploy         - Deploy to production"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make ps             - Show running containers"
	@echo "  make check          - Run Django system checks"
	@echo ""

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d
	@echo "Services started! Access at http://localhost"

# Stop services
down:
	docker-compose down

# Restart services
restart: down up

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-db:
	docker-compose logs -f db

logs-nginx:
	docker-compose logs -f nginx

# Django shell
shell:
	docker-compose exec backend python manage.py shell

# Bash shell
bash:
	docker-compose exec backend /bin/bash

# Database migrations
migrate:
	docker-compose exec backend python manage.py migrate

makemigrations:
	docker-compose exec backend python manage.py makemigrations

# Collect static files
collectstatic:
	docker-compose exec backend python manage.py collectstatic --noinput --clear

# Create superuser
createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

# Run tests
test:
	docker-compose exec backend pytest

test-backend:
	docker-compose exec backend pytest tests/

test-coverage:
	docker-compose exec backend pytest --cov=apps --cov-report=html

# Backup
backup:
	@chmod +x scripts/backup.sh
	@./scripts/backup.sh

# Restore (requires BACKUP_FILE variable)
restore:
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: BACKUP_FILE not specified"; \
		echo "Usage: make restore BACKUP_FILE=./backups/db_backup_20240101_120000.sql.gz"; \
		exit 1; \
	fi
	@gunzip -c $(BACKUP_FILE) | docker-compose exec -T db psql -U pms_user pms_production
	@echo "Database restored from $(BACKUP_FILE)"

# Deploy
deploy:
	@chmod +x scripts/deploy.sh
	@./scripts/deploy.sh

# Clean up
clean:
	docker-compose down -v
	@echo "All containers and volumes removed"

# Show container status
ps:
	docker-compose ps

# Django system checks
check:
	docker-compose exec backend python manage.py check

check-deploy:
	docker-compose exec backend python manage.py check --deploy

# Development commands
dev-build:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

dev-up:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-down:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
