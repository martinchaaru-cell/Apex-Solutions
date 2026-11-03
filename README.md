# Apex Solutions — website, admin dashboard and client portal

Flask, PostgreSQL (SQLite in development), Docker and Caddy. Built to **Level 2** of the Apex Security Baseline (logins and personal data).

- **Public website:** home, solutions (8 areas), industries, how we work, trust and security, our work, pricing, about, contact, privacy and terms.
- **Admin dashboard** (`/admin`): enquiries with status tracking and CSV export, client accounts, document uploads with sharing, and an activity log.
- **Client portal** (`/portal`): clients sign in and download the documents shared with them.

## Layout

Everything sits in the repository root, like Finance Intel and Match Oracle:

```
app.py            app factory, security headers, error pages, CLI commands
wsgi.py           production entry point (gunicorn wsgi:app)
config.py         settings from environment variables
extensions.py     database, CSRF and rate-limit objects
models.py         Enquiry, User, Token, Document, AuditLog
content.py        all public page copy, solution areas and prices
service_details.py  detailed description of every service (what, where used, capabilities, example, price)
routes.py         public website pages and contact form
auth.py           sign in, sign out, account setup, password reset and change
admin.py          admin dashboard
portal.py         client portal and the checked document download route
security.py       passwords, sessions, one-time links, role checks, audit log
storage.py        document upload checks and private storage
forms.py, mail.py
templates/        public pages, admin/, portal/, auth/
static/           css/, js/, fonts/, img/brand (logo), img/site (photos)
seed_documents/   Service Guide, agreements and templates, imported as admin-only documents on start
tests/            pytest suite (193 tests)
scripts/          replit-run.sh, backup.sh, restore-test.sh
docs/, security/  build spec and Security Baseline evidence checklist
```

Uploaded documents and the development database live in `instance/`, which is git-ignored and never committed.

## Run in Replit

1. Put all files and folders in the workspace root (no wrapper folder).
2. In **Tools > Secrets** add:
   - `ADMIN_EMAIL`: the email you will sign in with
   - `ADMIN_PASSWORD`: at least 12 characters (a phrase of three or four words works well)
   - `SECRET_KEY` (optional): if you skip it, the run script creates one in `.secret_key`
3. Press **Run**. The first run installs packages, imports the Service Guide as an admin-only document and creates your admin account from the two secrets.
4. Once you have signed in, delete the `ADMIN_PASSWORD` secret. It is only used to create the account and never changes an existing password. To change your name, open **My profile** in the dashboard. To change your password, use **Change password**.

   No secrets? You can still create the admin in the Shell with `flask --app app create-admin` (run `export SECRET_KEY=$(cat .secret_key)` first).
5. Open the site, click **Log in**, and sign in with that account.

Locked out? `flask --app app admin-reset-link you@example.com` prints a one-time reset link.

## Push to GitHub

From the Replit Shell (recommended, pushes every file including the dot-files):

```
git init            # only the first time
git add -A
git commit -m "Apex Solutions website and portal"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git   # only the first time
git push -u origin main
```

GitHub's web "Upload files" page accepts at most 100 files per upload and can skip hidden files such as `.gitignore`, `.replit` and `.github/`. If you upload through the browser, do it in two batches (for example `static/` first, then everything else) and add the dot-files with "Create new file".

## Using the dashboards

- **Add a client:** Admin > Clients > Add a client. You get a one-time link (valid 48 hours) to send to the client. They choose their own password. If SMTP is set up, the link is also emailed.
- **Share a document:** Admin > Documents > Upload. Choose **Admin only**, **All clients**, or **One client**. PDF, Word (.docx), Excel (.xlsx) and PowerPoint (.pptx) up to 20 MB. Macro-enabled files are refused.
- **Clients** see only the documents shared with all clients or with them, and every download is recorded in the activity log.

## Security in brief

Passwords hashed with scrypt; 12-character minimum with common passwords blocked; same error for unknown email and wrong password; lockout after 5 failures; rate-limited sign-in; sessions end after 15 minutes idle for admins, 30 for clients, 8 hours at most; changing a password signs out other devices; one-time links stored only as hashes; every admin route is admin-only by default; downloads are checked per document and per client; uploads are checked by extension and content, renamed, stored outside the web root and only ever sent as downloads; private pages are not cached or indexed.

**Recommended before going live:** two-step login (MFA) for admin accounts (Baseline A4) and an external review of the admin and portal.

## Run locally

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
export SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))")
export COOKIE_SECURE=false BEHIND_PROXY=false
flask --app app create-admin
flask --app app run
pytest -q
bandit -q -r . -x ./tests && pip-audit -r requirements.txt
```

## Deploy (Docker on a VPS)

1. Server: Ubuntu LTS, `ufw` default deny with 80, 443 and SSH from your IP only, SSH keys only, `unattended-upgrades`, `fail2ban`.
2. `cp .env.example .env` and fill it in (see the secrets list below).
3. Put your domain in `Caddyfile` and point DNS at the server.
4. `docker compose up -d --build`
5. `docker compose exec web flask --app app create-admin` and `docker compose exec web flask --app app import-seed-documents`
6. Set up `scripts/backup.sh` in cron (database and documents, encrypted, copied off the server) and run `scripts/restore-test.sh` once.
7. After a week of clean running, uncomment the HSTS line in `Caddyfile`.

**Secrets:** `SECRET_KEY` (always), `POSTGRES_PASSWORD` and `DATABASE_URL` (live server), `SMTP_PASSWORD` (if email is used), and the backup passphrase file.

## Deploy on Render

1. Push the code to GitHub (see above). In Render choose **New > Blueprint**, pick this repository, and it reads `render.yaml`. It creates the website (Starter plan with a 1 GB disk for uploaded documents) and a PostgreSQL database.
2. When asked, fill in `SITE_URL` (the `https://...onrender.com` address Render gives you, or your own domain later), `ADMIN_EMAIL`, `ADMIN_PASSWORD` and the contact and mail settings. `SECRET_KEY` and `DATABASE_URL` are filled in for you.
3. Deploy. The start script creates the admin from the two secrets and imports the documents in `seed_documents/`.
4. Sign in at `/login`, then delete the `ADMIN_PASSWORD` environment variable.
5. Never set `PREVIEW_MODE` on Render.

Free web and database plans are fine for a look around, but they lose uploaded documents on restart and the free database expires, so use paid plans for anything real.

## Day-to-day commands

| Task | Command |
|---|---|
| Create an admin | `flask --app app create-admin`, or set `ADMIN_EMAIL` and `ADMIN_PASSWORD` and run `flask --app app ensure-admin` |
| One-time reset link for any account | `flask --app app admin-reset-link email@example.com` |
| Import files in seed_documents/ | `flask --app app import-seed-documents` |
| Export enquiries to CSV | `flask --app app export-enquiries enquiries.csv` (or the button in Admin > Enquiries) |
| Delete one person's enquiries | `flask --app app delete-enquiry name@example.com` |
| Purge old enquiries (monthly) | `flask --app app purge-enquiries` |
