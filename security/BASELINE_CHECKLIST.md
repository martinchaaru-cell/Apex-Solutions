# Security Baseline — Level 1 evidence checklist (apexsolutions.co.ke)

Fill in the Evidence column before go-live and keep this file with the scan reports in `/security`.

| Control | What it means here | How it is met | Evidence |
|---|---|---|---|
| C2 | Server-side validation | WTForms validators, allow-listed choices, length limits, control-character and line-break checks | `tests/test_site.py::test_invalid_input_rejected` |
| C3 | Output encoding | Jinja auto-escaping, no `|safe` on user input | `test_xss_is_escaped` |
| C4 | CSRF | Flask-WTF token on the form; SameSite=Lax cookie | `test_csrf_required` |
| D1–D3 | Secrets out of code | All secrets from `.env`; `.env` in `.gitignore` and `.dockerignore`; gitleaks in CI | CI log |
| D6 | Strong app key | App refuses to start without a 32+ character `SECRET_KEY` | `test_refuses_to_start_without_strong_secret` |
| D7 | Debug off | Gunicorn in production, generic error pages | `test_debug_is_off`, `test_sensitive_paths_not_exposed` |
| E1 | HTTPS | Caddy automatic TLS; enable HSTS in `Caddyfile` after launch testing | SSL Labs grade (A expected) |
| E9 | Privacy notice | `/privacy` page; advocate review before launch | Advocate sign-off date |
| G1, G7 | Headers | CSP without unsafe-inline, nosniff, DENY framing, Referrer and Permissions policies | `test_security_headers`; securityheaders.com grade |
| G2 | No third-party scripts | Fonts and scripts self-hosted; CSP `'self'` only | `test_no_inline_script_or_style` |
| G3 | No exposed files | Only `/static` is served; unknown paths 404 | Exposed-files scan |
| G4 | Cookie flags | HttpOnly, Secure, SameSite=Lax | Browser devtools screenshot |
| G5 | Edge protection | Put Cloudflare (free plan) in front; restrict origin to Cloudflare IPs if practical | Config screenshot |
| G6 | Bot protection | Honeypot field plus rate limit (5/hour, 20/day per IP). Add Cloudflare Turnstile if spam appears | `test_honeypot_stores_nothing`, `test_rate_limit_on_post` |
| G8 | Mail header injection | Fixed From/To, fixed subject, single-line fields | `test_notification_uses_fixed_headers` |
| H1, H2 | Firewall and SSH | ufw default deny, allow 80/443 and SSH from your IP; keys only, no root, fail2ban | nmap result; `sshd_config` |
| H3 | Database not public | Postgres and Redis publish no ports in `docker-compose.yml` | nmap result |
| H6 | OS updates | `unattended-upgrades` enabled | Screenshot |
| H8 | Backups | `scripts/backup.sh` nightly, encrypted, copied off the server; `scripts/restore-test.sh` | Restore log with time taken |
| H9–H12 | Monitoring, domain, MFA | UptimeRobot on `/robots.txt`; registrar lock and MFA on registrar, Cloudflare, GitHub, server provider, email | Screenshots |
| I1, I2, I5 | Dependencies | Pinned requirements; pip-audit in CI; monthly update routine | CI log |
| J1, J5 | Logging and incident plan | Gunicorn access log, enquiry references logged without personal data; one-page incident plan | Plan in this folder |
| C11, E8 | Export and retention | Formula-safe CSV export; `flask purge-enquiries` monthly; `flask delete-enquiry` for requests | `test_export_and_delete_commands` |

## Level 2 additions (logins, dashboards, documents)

| Control | How it is met | Evidence |
|---|---|---|
| A1 | scrypt password hashing with per-user salt (werkzeug) | `test_passwords_are_hashed` |
| A2 | 12-character minimum, common and repetitive passwords blocked, email not allowed in password | `test_password_policy` |
| A3, A7 | Accounts set up by one-time link (48 h); resets 30 min; only a SHA-256 hash stored; single use | `test_setup_link_single_use`, `test_expired_link_rejected` |
| A5 | Login rate limit per IP (10/min, 50/h) plus 15-minute lockout after 5 failures per account | `test_login_rate_limited`, `test_lockout_after_repeated_failures` |
| A6 | Identical message for unknown email and wrong password; dummy hash check for timing; same response on forgot-password | `test_same_error_for_unknown_user_and_wrong_password`, `test_forgot_password_same_response` |
| A8 | HttpOnly, Secure, SameSite cookie; session cleared at login; 15/30-minute idle and 8-hour absolute timeouts; password change and disabling end all sessions | `test_session_cookie_flags`, `test_idle_timeout`, `test_change_password_ends_other_sessions`, `test_disabled_account_is_signed_out` |
| A10 | No seeded accounts; first admin by CLI only | `test_no_default_accounts` |
| B1, B2 | Admin blueprint guarded in `before_request` (deny by default); role checked on the server | `test_client_cannot_open_admin`, `test_logged_out_is_sent_to_login` |
| B3 | Per-document check `Document.visible_to`; other clients' files return 404 | `test_document_download_matrix`, `test_portal_lists_only_own_documents` |
| B5 | Forms only set allow-listed fields; role cannot be set from a request | `test_cannot_escalate_role_via_form` |
| B8 | Files stored in `instance/documents` (outside static), served only through the checked download route as attachments with `no-store` | `test_document_download_matrix` |
| C5 | Extension allow-list, content check (PDF header / Office ZIP parts), macro and zip-bomb checks, random names, 20 MB limit | `test_bad_uploads_rejected`, `test_macro_document_rejected`, `test_oversize_upload_rejected` |
| C9 | Display names stripped of paths; stored path confined to the documents folder | `test_path_in_filename_is_neutralised` |
| J1 | Audit log of sign-ins, failures, lockouts, uploads, downloads, denials and admin changes | `test_downloads_are_logged` |
| E6 | `Cache-Control: no-store` and `X-Robots-Tag: noindex` on all private pages | `test_private_pages_not_cached_or_indexed` |
| A4 (E) | Not yet: add TOTP two-step login for admins before go-live | Open item |
