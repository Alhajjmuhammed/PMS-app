#!/bin/bash

# ============================================
# PMS Backup Script
# ============================================

set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
MEDIA_BACKUP_FILE="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log_info "Starting backup process..."

# Backup database
log_info "Backing up database..."
docker-compose exec -T db pg_dump -U pms_user pms_production > "$DB_BACKUP_FILE"
gzip "$DB_BACKUP_FILE"
log_info "Database backed up to $DB_BACKUP_FILE.gz"

# Backup media files
log_info "Backing up media files..."
tar -czf "$MEDIA_BACKUP_FILE" -C ./backend media/
log_info "Media files backed up to $MEDIA_BACKUP_FILE"

# Clean up old backups (keep last 7 days)
log_info "Cleaning up old backups (keeping last 7 days)..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

log_info "Backup complete! 

Backup files:
- Database: $DB_BACKUP_FILE.gz
- Media: $MEDIA_BACKUP_FILE

To restore:
- Database: gunzip -c $DB_BACKUP_FILE.gz | docker-compose exec -T db psql -U pms_user pms_production
- Media: tar -xzf $MEDIA_BACKUP_FILE -C ./backend
"
