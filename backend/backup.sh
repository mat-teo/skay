#!/bin/bash
# Skay Finance - Database Backup Script
# Description: Creates a backup of the PostgreSQL database
# Usage: ./backup.sh


# Source the environment file if exists
if [ -f /app/.env ]; then
    set -a
    source /app/.env
    set +a
fi

# Also try to source from /etc/profile and /etc/environment
if [ -f /etc/environment ]; then
    set -a
    source /etc/environment
    set +a
fi

# Configuration
BACKUP_DIR="/app/backups"
DB_NAME="${POSTGRES_DB:-skay}"
DB_USER="${POSTGRES_USER:-skay_user}"
DB_PASSWORD="${POSTGRES_PASSWORD}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=7

mkdir -p $BACKUP_DIR

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting database backup..."

# Password is taken from environment variable $POSTGRES_PASSWORD
if [ -z $DB_PASSWORD ]; then
    log "ERROR: POSTGRES_PASSWORD environment variable not set"
    exit 1
fi

log "Backing up database: $DB_NAME"

PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h db \
    -U $DB_USER \
    -d $DB_NAME \
    -F c \
    -f "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

if [ $? -eq 0 ]; then
    log "Backup completed: ${DB_NAME}_${TIMESTAMP}.dump"
    SIZE=$(du -h "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump" | cut -f1)
    log "Size: $SIZE"
else
    log "ERROR: Backup failed!"
    exit 1
fi

# Clean old backups
find $BACKUP_DIR -name "*.dump" -type f -mtime +$RETENTION_DAYS -delete

BACKUP_COUNT=$(ls -1 $BACKUP_DIR/*.dump 2>/dev/null | wc -l)
log "Backups retained: $BACKUP_COUNT"

log "Backup completed"