#!/usr/bin/env bash
# Run the site in Replit so it shows in the Preview pane. Called by the Run button (.replit).
set -euo pipefail
cd "$(dirname "$0")/.."            # the workspace root

# Install packages only when requirements.txt changes.
STAMP=.replit-deps-installed
if [ ! -f "$STAMP" ] || [ requirements.txt -nt "$STAMP" ]; then
  echo "Installing packages..."
  pip install -q -r requirements.txt
  touch "$STAMP"
fi

# SECRET_KEY: best set in Replit Secrets (Tools > Secrets). If not set, create one once
# and keep it in a git-ignored file so sign-ins survive restarts.
if [ -z "${SECRET_KEY:-}" ]; then
  if [ ! -s .secret_key ]; then
    python -c "import secrets;print(secrets.token_urlsafe(48))" > .secret_key
    chmod 600 .secret_key
  fi
  export SECRET_KEY="$(cat .secret_key)"
fi

export PREVIEW_MODE="${PREVIEW_MODE:-true}"    # allow the Replit Preview pane to show the site
export BEHIND_PROXY="${BEHIND_PROXY:-true}"    # Replit's proxy sits in front of the app
export COOKIE_SECURE="${COOKIE_SECURE:-true}"  # the preview URL is HTTPS
export SITE_URL="${SITE_URL:-https://${REPLIT_DEV_DOMAIN:-localhost}}"

# Load the Service Guide (and any other files in seed_documents/) as admin-only documents.
flask --app app import-seed-documents || true

# Create the admin from the ADMIN_EMAIL and ADMIN_PASSWORD secrets (first run only).
flask --app app ensure-admin || true

if ! python -c "from app import create_app; from models import User; a=create_app(); a.app_context().push(); raise SystemExit(0 if User.query.filter_by(role='admin').count() else 1)" 2>/dev/null; then
  echo ""
  echo "No admin account yet. Add ADMIN_EMAIL and ADMIN_PASSWORD in Tools > Secrets and press Run again,"
  echo "or in the Shell run:  flask --app app create-admin"
  echo ""
fi

echo "Starting Apex Solutions on port 5000"
exec gunicorn -w 1 -b 0.0.0.0:5000 --forwarded-allow-ips='*' --access-logfile - wsgi:app
