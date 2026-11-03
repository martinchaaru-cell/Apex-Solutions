#!/usr/bin/env bash
# Nightly encrypted database backup (Baseline H8, E4).
# Cron example: 30 2 * * * /opt/apex-site/scripts/backup.sh >> /var/log/apex-backup.log 2>&1
# Needs BACKUP_PASSPHRASE_FILE (a root-only file) and an off-server copy step (rclone, s3cmd or scp).
set -euo pipefail
cd "$(dirname "$0")/.."
STAMP=$(date +%Y%m%d-%H%M)
OUT=backups/apex-$STAMP.sql.gz.gpg
mkdir -p backups && chmod 700 backups
: "${BACKUP_PASSPHRASE_FILE:?set BACKUP_PASSPHRASE_FILE}"

docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  | gzip \
  | gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase-file "$BACKUP_PASSPHRASE_FILE" -o "$OUT"

echo "$(date -Is) backup written: $OUT ($(du -h "$OUT" | cut -f1))"

# Uploaded documents (instance/documents) are backed up alongside the database.
DOCS=backups/apex-docs-$STAMP.tar.gz.gpg
docker compose exec -T web tar czf - -C /app/instance documents \
  | gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase-file "$BACKUP_PASSPHRASE_FILE" -o "$DOCS"
echo "$(date -Is) documents backup written: $DOCS"

# Copy off the server. Use credentials that cannot delete older copies.
# rclone copy "$OUT" offsite:apex-backups/

# Keep 14 days locally
find backups -name 'apex-*.gpg' -mtime +14 -delete
