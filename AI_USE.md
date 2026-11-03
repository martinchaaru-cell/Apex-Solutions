# AI use record (Apex Security Baseline K7)

| Date | Tool | Modules | Reviewer | Security review | Approved by |
|------|------|---------|----------|-----------------|-------------|
| 2026-11-02 | Claude (claude.ai) | Admin dashboard, client portal, auth, document storage (security.py, auth.py, admin.py, portal.py, storage.py) | Martin (to complete) | Pending: K1 line-by-line review of auth, permissions and uploads; K3 second AI review | Pending |
| 2026-11-02 | Claude (claude.ai) | Whole Phase 1 site: app factory, routes, contact form, templates, styles, Docker, CI | Martin (to complete) | Pending: run the Security Review Prompt (Baseline 9.2) in a separate session and triage findings | Pending |

Notes
- No secrets, production data or client personal data were given to the AI tool.
- All packages are well-known and pinned in `requirements.txt`, each with its purpose (I3).
- Code touching the enquiry form (validation, storage, email, export) must be read line by line before launch (K1).
