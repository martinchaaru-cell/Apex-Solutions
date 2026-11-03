#!/usr/bin/env bash
# Restore a backup into a throwaway database and count rows. Record the result and time taken.
set -euo pipefail
cd "$(dirname "$0")/.."
FILE=${1:?usage: restore-test.sh backups/apex-YYYYMMDD-HHMM.sql.gz.gpg}
: "${BACKUP_PASSPHRASE_FILE:?set BACKUP_PASSPHRASE_FILE}"
START=$(date +%s)
docker compose exec -T db sh -c 'dropdb -U "$POSTGRES_USER" --if-exists apex_restore_test && createdb -U "$POSTGRES_USER" apex_restore_test'
gpg --batch --decrypt --passphrase-file "$BACKUP_PASSPHRASE_FILE" "$FILE" | gunzip \
  | docker compose exec -T db sh -c 'psql -q -U "$POSTGRES_USER" apex_restore_test'
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" apex_restore_test -c "select count(*) as enquiries from enquiries;"'
docker compose exec -T db sh -c 'dropdb -U "$POSTGRES_USER" apex_restore_test'
echo "Restore test of $FILE passed in $(( $(date +%s) - START ))s on $(date -I)"
