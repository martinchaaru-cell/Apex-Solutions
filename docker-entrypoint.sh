#!/bin/sh
# Container start: prepare the documents folder, create the admin and import seed documents
# (both safe to repeat), then run the site as the unprivileged "apex" user.
set -eu
if [ "$(id -u)" = "0" ]; then export HOME=/home/apex; fi
DOCS="${DOCUMENTS_FOLDER:-/app/instance/documents}"
mkdir -p "$DOCS"

run() {
  if [ "$(id -u)" = "0" ]; then
    chown -R apex:apex "$DOCS"          # a mounted disk (for example on Render) starts owned by root
    chmod 700 "$DOCS"
    setpriv --reuid=10001 --regid=10001 --init-groups "$@"
  else
    "$@"
  fi
}

run flask --app app ensure-admin || true
run flask --app app import-seed-documents || true
exec_cmd="gunicorn -w ${WEB_CONCURRENCY:-3} -b 0.0.0.0:${PORT:-8000} --forwarded-allow-ips=* --access-logfile - wsgi:app"
if [ "$(id -u)" = "0" ]; then
  exec setpriv --reuid=10001 --regid=10001 --init-groups $exec_cmd
fi
exec $exec_cmd
