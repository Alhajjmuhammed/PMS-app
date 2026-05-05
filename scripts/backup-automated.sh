#!/bin/bash
#
# Hotel PMS - Automated Backup Script
# Backs up PostgreSQL database and media files
#
# Usage:  ./backup.sh
# Schedule with CRON: 0 2 * * * /path/to/backup.sh
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/backend/.env"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Backup configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/hotel_pms}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_DIR=$(date +"%Y-%m-%d")

# Database configuration
DB_NAME="${DATABASE_NAME:-hotel_pms}"
DB_USER="${DATABASE_USER:-postgres}"
DB_HOST="${DATABASE_HOST:-localhost}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_PASSWORD="${DATABASE_PASSWORD}"

# Paths
DB_BACKUP_DIR="$BACKUP_DIR/database/$DATE_DIR"
MEDIA_BACKUP_DIR="$BACKUP_DIR/media/$DATE_DIR"
LOG_FILE="$BACKUP_DIR/backup.log"

# =============================================================================
# FUNCTIONS
# =============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error_exit() {
    log "ERROR: $1"
    exit 1
}

create_backup_dirs() {
    log "Creating backup directories..."
    mkdir -p "$DB_BACKUP_DIR" || error_exit "Failed to create database backup directory"
    mkdir -p "$MEDIA_BACKUP_DIR" || error_exit "Failed to create media backup directory"
    mkdir -p "$(dirname "$LOG_FILE")" || error_exit "Failed to create log directory"
}

backup_database() {
    log "Starting database backup..."
    
    DB_BACKUP_FILE="$DB_BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"
    
    # Export password for pg_dump
    export PGPASSWORD="$DB_PASSWORD"
    
    # Create database dump
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --no-owner --no-acl --clean --if-exists \
        | gzip > "$DB_BACKUP_FILE" \
        || error_exit "Database backup failed"
    
    unset PGPASSWORD
    
    # Get file size
    DB_SIZE=$(du -h "$DB_BACKUP_FILE" | cut -f1)
    log "Database backup completed: $DB_BACKUP_FILE ($DB_SIZE)"
    
    # Create a "latest" symlink
    ln -sf "$DB_BACKUP_FILE" "$BACKUP_DIR/database/latest.sql.gz"
}

backup_media() {
    log "Starting media files backup..."
    
    MEDIA_DIR="$PROJECT_ROOT/backend/media"
    MEDIA_BACKUP_FILE="$MEDIA_BACKUP_DIR/media_${TIMESTAMP}.tar.gz"
    
    if [ -d "$MEDIA_DIR" ] && [ "$(ls -A $MEDIA_DIR)" ]; then
        tar -czf "$MEDIA_BACKUP_FILE" -C "$MEDIA_DIR" . \
            || error_exit "Media backup failed"
        
        MEDIA_SIZE=$(du -h "$MEDIA_BACKUP_FILE" | cut -f1)
        log "Media backup completed: $MEDIA_BACKUP_FILE ($MEDIA_SIZE)"
        
        # Create a "latest" symlink
        ln -sf "$MEDIA_BACKUP_FILE" "$BACKUP_DIR/media/latest.tar.gz"
    else
        log "No media files to backup (directory empty or doesn't exist)"
    fi
}

cleanup_old_backups() {
    log "Cleaning up backups older than $BACKUP_RETENTION_DAYS days..."
    
    # Clean old database backups
    find "$BACKUP_DIR/database" -type f -name "*.sql.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
    DB_DELETED=$(find "$BACKUP_DIR/database" -type d -empty -delete 2>&1 | wc -l)
    
    # Clean old media backups
    find "$BACKUP_DIR/media" -type f -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
    MEDIA_DELETED=$(find "$BACKUP_DIR/media" -type d -empty -delete 2>&1 | wc -l)
    
    log "Cleanup completed. Removed old backups."
}

verify_backup() {
    log "Verifying backup integrity..."
    
    # Verify database backup
    if [ -f "$DB_BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz" ]; then
        if gzip -t "$DB_BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz" 2>/dev/null; then
            log "Database backup verification: OK"
        else
            error_exit "Database backup verification failed (corrupted file)"
        fi
    fi
}

send_notification() {
    local STATUS=$1
    local MESSAGE=$2
    
    # Send notification email (if configured)
    if command -v mail &> /dev/null && [ ! -z "${BACKUP_EMAIL:-}" ]; then
        echo "$MESSAGE" | mail -s "Hotel PMS Backup $STATUS" "$BACKUP_EMAIL"
    fi
    
    # Log to system log
    logger -t hotel_pms_backup "$STATUS: $MESSAGE"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

log "=========================================="
log "Hotel PMS Backup Started"
log "=========================================="

# Check if PostgreSQL tools are installed
if ! command -v pg_dump &> /dev/null; then
    error_exit "pg_dump not found. Please install PostgreSQL client tools."
fi

# Create backup directories
create_backup_dirs

# Perform backups
backup_database
backup_media

# Verify backups
verify_backup

# Cleanup old backups
cleanup_old_backups

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR/$DATE_DIR" | cut -f1)

log "=========================================="
log "Backup completed successfully!"
log "Total size: $TOTAL_SIZE"
log "Location: $BACKUP_DIR/$DATE_DIR"
log "=========================================="

# Send success notification
send_notification "SUCCESS" "Backup completed. Size: $TOTAL_SIZE, Location: $BACKUP_DIR/$DATE_DIR"

exit 0
