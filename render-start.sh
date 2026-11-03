#!/usr/bin/env bash
# Start command on Render: set up the admin and seed documents, then run the site.
set -euo pipefail
mkdir -p "${DOCUMENTS_FOLDER:-instance/documents}"
flask --app app ensure-admin || true
flask --app app import-seed-documents || true
exec gunicorn -w 1 --threads 4 -b 0.0.0.0:${PORT:-10000} --forwarded-allow-ips='*' --access-logfile - wsgi:app
