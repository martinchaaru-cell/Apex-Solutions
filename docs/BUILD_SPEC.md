# Apex Solutions website — Phase 1 build spec

Version 1.0, 2 November 2026. Risk level: **Security Baseline Level 2** (admin and client logins, client documents, contact form).

## 1. Sitemap (Phase 1)

| # | Page | URL |
|---|------|-----|
| 1 | Home | `/` |
| 2 | Solutions overview | `/solutions` |
| 3 | Business systems and web apps | `/solutions/business-systems` |
| 4 | POS systems | `/solutions/pos-systems` |
| 5 | Websites and e-commerce | `/solutions/websites-ecommerce` |
| 6 | Payments and integrations (M-Pesa, cards, eTIMS) | `/solutions/integrations` |
| 7 | Hosting and maintenance | `/solutions/hosting-maintenance` |
| 8 | How we work (process + trust and security) | `/how-we-work` |
| 9 | Our work (portfolio) | `/our-work` and `/our-work/<slug>` |
| 10 | Retail and hospitality | `/industries/retail-hospitality` |
| 11 | Education | `/industries/education` |
| 12 | Pricing | `/pricing` |
| 13 | About | `/about` |
| 14 | Contact | `/contact` |
| 15 | Privacy notice | `/privacy` |
| 16 | Terms of use | `/terms` |

Plus `robots.txt`, `sitemap.xml`, `/.well-known/security.txt` (Baseline J9) and a 404 page.

**Navigation:** Home · Solutions · Industries · Our Work · Company (How we work, About) · Pricing · Contact. Primary button: "Request a proposal".

**Deferred to Phase 2:** AI and Data pages, more industries, Insights, find-a-solution tool, live demo, client portal.

## 2. Copy rules (enforced by `tests/test_site.py::test_no_banned_claims`)

1. No certification, compliance or accreditation Apex does not hold (ISO, PCI, GDPR, SOC). Say "Built to the Apex Security Baseline".
2. No invented numbers: project counts, satisfaction percentages, client counts, uptime guarantees.
3. No "unhackable", "100% secure", "bank-grade", "enterprise-grade", "24/7" (except where a signed plan offers it).
4. No team photos, office buildings or addresses that are not real. Contact details come from environment variables and are hidden when unset.
5. Portfolio shows only real work, labelled with its true status (live, MVP, proof of concept, in development). No results unless verified.
6. Every price is a starting range from the Pricing Guide, marked "excl. 16% VAT".
7. Tier 2 and Tier 3 services are described as "by consultation" or "coming", never as ready products.

## 3. Design tokens

| Token | Value | Use |
|-------|-------|-----|
| `--navy-900` | `#0B1F44` | Headings, footer, dark bands |
| `--navy-700` | `#13306B` | Secondary dark |
| `--cobalt-600` | `#1D5BEA` | Primary buttons, links |
| `--cobalt-700` | `#1747BC` | Hover |
| `--sky-100` | `#E8F0FE` | Tinted panels, chips |
| `--sky-50` | `#F4F8FF` | Section background |
| `--ink-900` | `#16202E` | Body text |
| `--ink-600` | `#4A5568` | Secondary text |
| `--line` | `#DCE4F0` | Borders |
| `--ok` | `#0E8A5F` | Ticks |

Type: Plus Jakarta Sans, self-hosted (400–800). Scale: 14 / 16 / 18 / 22 / 28 / 36 / 48 px. Radius 14px cards, 999px buttons. Max width 1180px. Line icons only, 1.75 stroke.

Visuals are built in HTML/CSS (illustrative product frames with clearly fictional sample data), not stock photos. Real screenshots go in `app/static/img/work/<slug>.webp` and replace the illustration automatically.

## 3b. Dashboards (v4, 2 November 2026)

- Admin dashboard at `/admin`: overview, enquiries (status, CSV export), clients (one-time setup links, disable), documents (upload, share with admin only, all clients or one client), activity log.
- Client portal at `/portal`: documents shared with the client, download, change password.
- First admin created only through `flask --app app create-admin` (A10). No self-registration.
- Logo: from the supplied artwork (`static/img/brand/`), header in colour and footer in white.

## 3a. Design (v3, 2 November 2026)

The site follows the approved mockups: photo heroes fading into a light background, outlined label chips, image cards, numbered process cards and rounded navy CTA bands. The photography in `app/static/img/site/` is cropped from those AI-generated mockups and is a placeholder for the preview.

The full catalogue is listed in eight solution areas, each marked Available now (Tier 1), By consultation (Tier 2) or Specialist or partner-led (Tier 3), with every price line from the Service Guide.

## 4. Before launch — confirm with Martin

- [ ] Add two-step login (MFA) for admin accounts (Baseline A4).
- [ ] Upload the original Word documents (agreements, proposal template, questionnaire, security baseline) through Admin > Documents and choose who sees each.

- [ ] Replace the mockup photography with real photos of the Apex team and real project screenshots. The team photos and the branded office imagery must show people and places that exist.
- [ ] Permission to show the bar and lounge POS and the school system, and whether to name those clients.

- [ ] Permission to name QT Ladies Collection, and screenshots for it, Finance Intel and Match Oracle.
- [ ] Real contact email, phone, WhatsApp number and location wording (set in `.env`).
- [ ] Privacy notice and terms reviewed by a Kenyan advocate (Baseline E9).
- [ ] Domain, Cloudflare and SMTP accounts in Apex Solutions' name, with MFA (H10, H12).
- [ ] Confirm the reply-time promise on the contact page ("usually within one business day") is one you can keep.
- [ ] Confirm the hosting provider and region, and update the privacy notice if personal data will be stored outside Kenya.
