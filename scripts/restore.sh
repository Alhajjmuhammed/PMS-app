#!/bin/bash
#
# Hotel PMS - Restore from Backup Script
# Restores PostgreSQL database and media files from backup
#
# Usage: ./restore.sh [backup_date]
# Example: ./restore.sh 2026-04-14
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

# Database configuration
DB_NAME="${DATABASE_NAME:-hotel_pms}"
DB_USER="${DATABASE_USER:-postgres}"
DB_HOST="${DATABASE_HOST:-localhost}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_PASSWORD="${DATABASE_PASSWORD}"

# Parse arguments
BACKUP_DATE=${1:-"latest"}

# =============================================================================
# FUNCTIONS
# =============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error_exit() {
    log "ERROR: $1"
    exit 1
}

list_available_backups() {
    log "Available backups:"
    ls -lh "$BACKUP_DIR/database/" | grep -E "^d" | awk '{print $9}'
}

confirm_restore() {
    read -p "⚠️  WARNING: This will OVERWRITE the current database. Continue? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        log "Restore cancelled by user"
        exit 0
    fi
}

restore_database() {
    log "Restoring database..."
    
    # Find backup file
    if [ "$BACKUP_DATE" = "latest" ]; then
        DB_BACKUP_FILE="$BACKUP_DIR/database/latest.sql.gz"
    else
        DB_BACKUP_FILE=$(find "$BACKUP_DIR/database/$BACKUP_DATE" -name "*.sql.gz" | head -1)
    fi
    
    if [ ! -f "$DB_BACKUP_FILE" ]; then
        error_exit "Backup file not found: $DB_BACKUP_FILE"
    fi
    
    log "Using backup file: $DB_BACKUP_FILE"
    
    # Export password for psql
    export PGPASSWORD="$DB_PASSWORD"
    
    # Restore database
    gunzip -c "$DB_BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        || error_exit "Database restore failed"
    
    unset PGPASSWORD
    
    log "Database restored successfully"
}

restore_media() {
    log "Restoring media files..."
    
    # Find media backup file
    if [ "$BACKUP_DATE" = "latest" ]; then
        MEDIA_BACKUP_FILE="$BACKUP_DIR/media/latest.tar.gz"
    else
        MEDIA_BACKUP_FILE=$(find "$BACKUP_DIR/media/$BACKUP_DATE" -name "*.tar.gz" | head -1)
    fi
    
    if [ ! -f "$MEDIA_BACKUP_FILE" ]; then
        log "WARNING: Media backup file not found: $MEDIA_BACKUP_FILE"
        return
    fi
    
    log "Using media backup: $MEDIA_BACKUP_FILE"
    
    MEDIA_DIR="$PROJECT_ROOT/backend/media"
    
    # Backup current media (just in case)
    if [ -d "$MEDIA_DIR" ] && [ "$(ls -A $MEDIA_DIR)" ]; then
        TEMP_BACKUP="/tmp/media_backup_$(date +%s).tar.gz"
        tar -czf "$TEMP_BACKUP" -C "$MEDIA_DIR" .
        log "Current media backed up to: $TEMP_BACKUP"
    fi
    
    # Clear and restore media
    rm -rf "$MEDIA_DIR"
    mkdir -p "$MEDIA_DIR"
    tar -xzf "$MEDIA_BACKUP_FILE" -C "$MEDIA_DIR"
    
    log "Media files restored successfully"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

log "=========================================="
log "Hotel PMS Restore Process"
log "=========================================="

# List backups if requested
if [ "$BACKUP_DATE" = "list" ]; then
    list_available_backups
    exit 0
fi

# Confirm restore
confirm_restore

# Check if PostgreSQL tools are installed
if ! command -v psql &> /dev/null; then
    error_exit "psql not found. Please install PostgreSQL client tools."
fi

# Perform restore
restore_database
restore_media

log "=========================================="
log "Restore completed successfully!"
log "=========================================="

exit 0
