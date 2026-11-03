"""All page copy in one place, so wording can be changed without touching templates.

Sources: Apex Service Catalogue, Delivery Blueprint and Pricing Guide v1.1 (Oct 2026),
Security Baseline v1.0 and the Hosting and Maintenance Agreement.
Copy rules are in docs/BUILD_SPEC.md and enforced by tests.

Availability follows the launch tiers in the Service Guide:
  NOW        = Tier 1, launch now
  CONSULT    = Tier 2, offered case by case while packages are built
  SPECIALIST = Tier 3, specialist service or delivered with a certified partner
"""

NOW = "Available now"
CONSULT = "By consultation"
SPECIALIST = "Specialist or partner-led"

VAT_NOTE = "All prices are starting ranges in Kenya shillings and exclude 16% VAT."
QUOTED = "Quoted per project"

# ---------------------------------------------------------------------------
# Solutions: the full catalogue (Service Guide section 2), grouped as in the designs.
# Each price row: (service, typical inclusions, price KES excl. VAT, timeline, availability)
# ---------------------------------------------------------------------------
SOLUTIONS = {
    "software-development": {
        "slug": "software-development",
        "explore": "Explore Software",
        "icon": "code",
        "image": "svc-software",
        "hero": "hero-individual",
        "title": "Custom software development",
        "nav_title": "Custom Software Development",
        "short": "Web apps, ERP, CRM, inventory, HR and payroll, school, SACCO and booking systems, and mobile apps.",
        "lede": "Replace spreadsheets, notebooks and WhatsApp threads with one system your whole team uses, with the right access for each person.",
        "availability": NOW,
        "security": "Level 2, or Level 3 for school, SACCO and clinic systems",
        "support": "Standard plan",
        "problems": [
            "Records live in Excel files that only one person understands.",
            "Approvals happen by phone and nobody can see who changed what.",
            "Month-end reports take days to compile by hand.",
            "Off-the-shelf software forces you to change how you work.",
        ],
        "features": [
            ("users", "Roles and permissions", "Each person sees and edits only what their job needs, checked on the server for every request."),
            ("flow", "Workflows and approvals", "Your real process written as steps, with approvals and an audit trail of who did what and when."),
            ("chart", "Reports and exports", "Dashboards plus Excel and PDF exports of the reports you already use."),
            ("plug", "Integrations", "M-Pesa, SMS and email notifications, and links to the tools you already have."),
            ("doc", "Data import", "Your existing records cleaned, mapped and imported, with a reconciliation check."),
            ("phone", "Web and mobile", "Browser-based systems first, then installable web apps and Android and iOS apps when you need them."),
        ],
        "examples": ["ERP and CRM", "Inventory and procurement", "HR and payroll", "School management", "SACCO and cooperative systems", "Hospital and clinic systems", "Property management", "Booking and membership", "Desktop apps", "Android and iOS apps"],
        "prices": [
            ("Custom web app (portal, booking, dashboard)", "Roles, database, admin panel, API", "150,000 – 500,000", "6–12 weeks", NOW),
            ("Business system (inventory, HR, payroll, CRM, procurement)", "Modules, reports, roles, audit log", "200,000 – 600,000", "8–14 weeks", NOW),
            ("School, SACCO or clinic management system", "Multi-module, SMS, M-Pesa, reports", "300,000 – 800,000", "10–16 weeks", NOW),
            ("Progressive web app (PWA)", "Installable, basic offline, push notifications", "100,000 – 250,000", "4–8 weeks", CONSULT),
            ("Android, iOS or cross-platform app", "Both stores, push, backend API, store submission", "250,000 – 800,000", "8–16 weeks", CONSULT),
            ("Hospital systems and desktop apps", "Scoped with enhanced security review", QUOTED, "As agreed", SPECIALIST),
        ],
    },
    "pos-systems": {
        "slug": "pos-systems",
        "explore": "Explore POS",
        "icon": "pos",
        "image": "svc-pos",
        "hero": "work-pos",
        "title": "POS systems",
        "nav_title": "POS Systems",
        "short": "Retail, restaurant, bar, hotel and pharmacy point of sale with stock, M-Pesa, eTIMS and reports.",
        "lede": "A fast sales screen for your cashiers, accurate stock for your manager, and today's figures on the owner's phone.",
        "availability": NOW,
        "security": "Level 3, high risk",
        "support": "POS Care plan",
        "problems": [
            "Stock counts take days and losses are hard to trace.",
            "You cannot see sales when you are away from the shop.",
            "M-Pesa payments are confirmed by checking messages one by one.",
            "eTIMS invoices are typed in by hand.",
        ],
        "features": [
            ("pos", "Fast sales screen", "Barcode and manual entry, weighed items, discounts, held sales, returns and receipts."),
            ("box", "Stock and suppliers", "Stock deducts on every sale, with goods received, supplier records, counts and low-stock alerts."),
            ("card", "M-Pesa and cards", "STK push with automatic reconciliation. Payments are confirmed with the provider before a sale closes."),
            ("doc", "KRA eTIMS", "Tax invoice integration for VAT-registered businesses, confirmed with each client's accountant."),
            ("users", "Staff controls", "Cashier, manager and owner roles. Voids and refunds need a reason and approval, and are logged."),
            ("wifi", "Works through outages", "Sales continue through internet drops and power cuts and sync when the connection returns."),
        ],
        "examples": ["Supermarkets and shops", "Hardware stores", "Restaurants and cafes", "Bars and lounges", "Hotels", "Pharmacies", "Electronics", "Wholesale counters", "Loyalty and customer accounts"],
        "prices": [
            ("Retail POS (shop, minimart)", "Sales, receipts, stock, reports, users", "80,000 – 250,000", "4–8 weeks", NOW),
            ("Restaurant or bar POS", "Tables, kitchen tickets, split bills, stock", "120,000 – 350,000", "6–10 weeks", NOW),
            ("Pharmacy or specialised POS", "Batch and expiry tracking, suppliers", "150,000 – 400,000", "6–10 weeks", NOW),
            ("Fuel station POS", "Pump, shift and tank reconciliation", QUOTED, "As agreed", SPECIALIST),
        ],
        "note": "Hardware (PCs, receipt printers, scanners, cash drawers and a UPS) is supplied by you. We test our software with the exact models you list. For businesses that cannot trade when the till is down, we offer the POS Care support plan with seven-day trading-hours cover.",
    },
    "websites-ecommerce": {
        "slug": "websites-ecommerce",
        "explore": "Explore Web Solutions",
        "icon": "cart",
        "image": "svc-web",
        "hero": "hero-solutions",
        "title": "Websites and e-commerce",
        "nav_title": "Websites & E-commerce",
        "short": "Corporate, NGO, school and government websites, and online stores with M-Pesa and card checkout.",
        "lede": "A fast, secure website you can update yourself, or an online store that takes M-Pesa and card payments.",
        "availability": NOW,
        "security": "Level 1 for sites, Level 2–3 for stores",
        "support": "Basic or Standard plan",
        "problems": [
            "Customers cannot find you, or find an outdated site.",
            "Every small text change needs a developer.",
            "Orders arrive on WhatsApp and get lost.",
            "Payments are confirmed manually before goods leave.",
        ],
        "features": [
            ("phone", "Fast on any phone", "Responsive layouts that load in under three seconds on a typical mobile connection."),
            ("pen", "Edit it yourself", "A simple admin or CMS so you can change text, images and prices without calling us."),
            ("search", "Search basics done", "Titles, descriptions, sitemap, Google Business Profile and Search Console set up."),
            ("cart", "Online store", "Catalogue, cart, checkout, order emails, stock tracking and discount codes."),
            ("card", "Payments you can trust", "Totals are calculated on the server and an order is marked paid only after the provider confirms."),
            ("shield", "Protected forms", "Spam protection, SSL and security headers on every site."),
        ],
        "examples": ["Corporate websites", "NGO and government sites", "School websites", "Online stores", "Marketplaces", "News portals and blogs", "Membership platforms", "Learning platforms"],
        "prices": [
            ("Landing page or starter site (up to 5 pages)", "Responsive design, contact form, basic SEO", "15,000 – 40,000", "1–2 weeks", NOW),
            ("Business or corporate website (5–10 pages, CMS)", "Editable content, SEO setup, analytics", "50,000 – 120,000", "2–4 weeks", NOW),
            ("NGO, school or institutional website", "Multi-section, news, downloads, forms", "80,000 – 200,000", "3–6 weeks", NOW),
            ("E-commerce store", "Catalogue, cart, M-Pesa and card checkout, order admin", "100,000 – 300,000", "4–8 weeks", NOW),
            ("SEO, analytics setup and documentation", "Optimisation, manuals, knowledge bases", QUOTED, "As agreed", CONSULT),
        ],
    },
    "ai-automation": {
        "slug": "ai-automation",
        "explore": "Explore AI Solutions",
        "icon": "chip",
        "image": "svc-ai",
        "hero": "hero-capabilities",
        "title": "AI and automation",
        "nav_title": "AI & Automation",
        "short": "Chatbots and knowledge assistants on your own documents, OCR and invoice extraction, and AI search.",
        "lede": "Put AI to work on the documents and questions your team handles every day, with a human review step where it matters.",
        "availability": CONSULT,
        "security": "Level 3, with prompt-injection testing",
        "support": "Standard or Premium plan",
        "problems": [
            "Staff answer the same customer questions all day.",
            "Invoices and forms are re-typed from PDFs by hand.",
            "Policies and reports are hard to search.",
            "Nobody has time to read every contract and report in full.",
        ],
        "features": [
            ("chat", "Chatbots and assistants", "Answers drawn from your own documents, on your website or WhatsApp."),
            ("doc", "Document extraction", "OCR and PDF extraction for invoices, forms and reports, with a review screen before data is saved."),
            ("search", "AI search", "Find the right policy, contract or record by asking in plain language."),
            ("users", "Human review", "Legal, financial and medical output is reviewed by a person before it is used."),
            ("lock", "Your data stays yours", "Retrieval respects each user's permissions, and providers are checked so they do not train on your data."),
            ("tag", "Clear running costs", "A cost estimate for monthly AI usage, with spending caps, before you commit."),
        ],
        "examples": ["Customer support bots", "Internal knowledge assistants", "Invoice and PDF extraction", "Contract and report analysis", "AI search", "Recommendations", "Predictive analytics"],
        "prices": [
            ("AI chatbot or knowledge assistant", "Trained on your documents, web or WhatsApp channel", "60,000 – 200,000", "3–6 weeks", CONSULT),
            ("Document extraction (OCR, PDF, invoices)", "Extraction, review screen, export", "100,000 – 350,000", "4–10 weeks", CONSULT),
            ("Recommendations and predictive analytics", "Scoped after a data review", QUOTED, "As agreed", CONSULT),
        ],
        "note": "Every AI project starts with a defined scope and a test set of real questions or documents with expected answers, so you can see how accurate it is before go-live.",
    },
    "data-intelligence": {
        "slug": "data-intelligence",
        "explore": "Explore Analytics",
        "icon": "chart",
        "image": "svc-data",
        "hero": "work-bi",
        "title": "Data and business intelligence",
        "nav_title": "Data & Business Intelligence",
        "short": "KPI and executive dashboards, automated reports, data integration, and finance and governance intelligence.",
        "lede": "Turn the data you already hold into dashboards and reports you can trust, with every figure traceable to its source.",
        "availability": CONSULT,
        "security": "Level 2, with row-level access to data",
        "support": "Standard plan",
        "problems": [
            "Reports are rebuilt by hand every month.",
            "Different teams quote different numbers for the same thing.",
            "Management cannot see performance until it is too late to act.",
            "Board and pay benchmarking takes weeks of reading annual reports.",
        ],
        "features": [
            ("chart", "Dashboards", "Executive, KPI and operational dashboards with filters and drill-down."),
            ("doc", "Automated reports", "Scheduled performance and compliance reports by PDF, Excel or email."),
            ("flow", "Data integration", "Data pulled together from your systems, with quality checks and reconciliation against source totals."),
            ("users", "Role-based access", "Each person sees the data their role allows."),
            ("search", "Defined metrics", "Every KPI written down with how it is calculated, so numbers mean the same thing to everyone."),
            ("briefcase", "Governance intelligence", "Director remuneration, board composition and ESG benchmarking from company filings."),
        ],
        "examples": ["Executive dashboards", "KPI tracking", "Operational reports", "Compliance reports", "Data warehousing", "Data migration", "Director remuneration surveys", "ESG reporting"],
        "prices": [
            ("Dashboards and BI reporting", "KPIs, charts, exports, scheduled reports", "50,000 – 250,000", "2–6 weeks", CONSULT),
            ("Finance Intel report (per company or sector)", "Remuneration, governance or ESG analysis", "30,000 – 150,000", "1–3 weeks", SPECIALIST),
            ("Data warehousing and integration", "Source mapping, refresh schedule, reconciliation", QUOTED, "As agreed", CONSULT),
            ("Data migration and import", "Cleaning, mapping, validation, reconciliation", "20,000 – 100,000", "1–3 weeks", NOW),
        ],
    },
    "cloud-hosting": {
        "slug": "cloud-hosting",
        "explore": "Explore Cloud Services",
        "icon": "cloud",
        "image": "svc-cloud",
        "hero": "hero-work",
        "title": "Cloud, hosting and maintenance",
        "nav_title": "Cloud, Hosting & Maintenance",
        "short": "Website, app and VPS hosting, Docker deployment, cloud migration, backups, monitoring and support plans.",
        "lede": "Software needs looking after. We host it, back it up, keep it updated and respond when something goes wrong.",
        "availability": NOW,
        "security": "Hardened server, tested backups",
        "support": "Basic to Premium, or POS Care",
        "problems": [
            "Nobody knows whether backups work until data is lost.",
            "Security updates are never applied.",
            "The domain expires or sits in a former developer's name.",
            "When the system goes down there is no one to call.",
        ],
        "features": [
            ("server", "Docker deployment", "Your application on a server we manage, with SSL, a default-deny firewall and the database never exposed to the internet."),
            ("refresh", "Backups you can restore", "Daily encrypted backups copied off the server, with restore tests on a schedule."),
            ("pulse", "Monitoring", "Uptime, errors and SSL expiry are monitored, with alerts sent to a named person."),
            ("shield", "Updates", "Operating system and dependency updates, with critical security patches applied promptly."),
            ("key", "Your accounts, your name", "Domains and third-party accounts stay registered to you."),
            ("support", "Clear response times", "Each plan states its response targets for critical, major and minor issues."),
        ],
        "examples": ["Website hosting", "App and POS hosting", "VPS and server setup", "Docker deployment", "Database hosting", "Cloud migration", "Backups and restore tests", "Support plans"],
        "prices": [
            ("Cloud setup and Docker deployment (one-off)", "Server, Docker, SSL, backups, monitoring", "20,000 – 70,000", "2–5 days", NOW),
            ("Cloud migration", "Move an existing system to a managed server", QUOTED, "As agreed", CONSULT),
        ],
        "show_plans": True,
    },
    "integrations-consulting": {
        "slug": "integrations-consulting",
        "explore": "Explore Consulting",
        "icon": "puzzle",
        "image": "svc-integrations",
        "hero": "img-handshake",
        "title": "Integrations and IT consulting",
        "nav_title": "Integrations & IT Consulting",
        "short": "M-Pesa, card gateways, KRA eTIMS, SMS, ERP and accounting integrations, and expert IT advice.",
        "lede": "Connect your systems to M-Pesa, payment gateways, eTIMS and each other, and get clear advice before you buy or build.",
        "availability": NOW,
        "security": "Level 3, high risk",
        "support": "Standard or POS Care plan",
        "problems": [
            "Staff reconcile M-Pesa statements against sales by hand.",
            "A fake payment message could release goods.",
            "Tax invoices are re-typed into another system.",
            "You are not sure which software to buy, or whether to build.",
        ],
        "features": [
            ("phone", "M-Pesa Daraja", "STK push, callbacks and reconciliation on your own Paybill or Till. We never hold client funds."),
            ("shield", "Verified payments", "Callbacks are treated as unconfirmed until checked with Safaricom or the gateway, and each transaction is processed once."),
            ("card", "Card gateways", "Checkout using the gateway's hosted fields, with webhooks and refunds."),
            ("doc", "KRA eTIMS", "Electronic tax invoices for VAT-registered businesses, scoped with your accountant."),
            ("flow", "Systems that talk", "ERP, CRM, accounting, SMS and email connected through REST and internal APIs."),
            ("compass", "IT consulting", "Technology strategy, software selection, architecture, database design and infrastructure planning."),
        ],
        "examples": ["M-Pesa STK push", "Paybill and Till reconciliation", "Card checkout", "KRA eTIMS", "Bulk SMS", "Accounting integrations", "ERP and CRM integrations", "System audits", "Technology strategy"],
        "prices": [
            ("M-Pesa (Daraja) integration", "STK push, callbacks, reconciliation, go-live support", "30,000 – 80,000", "1–3 weeks", NOW),
            ("Card gateway integration", "Checkout, webhooks, refunds", "30,000 – 100,000", "1–3 weeks", NOW),
            ("KRA eTIMS integration", "Quoted with the POS or invoicing system", QUOTED, "Depends on scope", NOW),
            ("ERP, CRM, accounting and bank API integrations", "Sandbox testing, then production go-live", QUOTED, "As agreed", CONSULT),
            ("IT consulting or system audit", "Or KES 25,000 – 60,000 per day", "3,000 – 6,000 per hour", "As agreed", CONSULT),
        ],
        "note": "Access to your M-Pesa, eTIMS, SMS and gateway accounts is confirmed in the first week of a project, because live transactions are tested before go-live. Safaricom and provider approvals are outside our control and can affect dates.",
    },
    "cybersecurity": {
        "slug": "cybersecurity",
        "explore": "Explore Security",
        "icon": "shield",
        "image": "svc-security",
        "hero": "hero-trust",
        "title": "Cybersecurity solutions",
        "nav_title": "Cybersecurity Solutions",
        "short": "Penetration testing and security audits through a certified partner, plus backups, recovery and access control.",
        "lede": "Every system we build is secured to the Apex Security Baseline. For independent testing and audits of your wider estate, we work with a certified partner.",
        "availability": SPECIALIST,
        "security": "Partner-led, with written authorisation",
        "support": "Premium plan for quarterly reviews",
        "problems": [
            "You have never had your systems tested by someone independent.",
            "Former staff may still have access.",
            "Backups exist, but no one has tried restoring one.",
            "There is no plan for what to do if you are breached.",
        ],
        "features": [
            ("search", "Penetration testing", "External testing with written authorisation from the system owner, a findings report and a retest after fixes."),
            ("doc", "Security audits", "A review of your systems and practices against a written standard, with prioritised recommendations."),
            ("refresh", "Backup and recovery", "Encrypted, off-server backups with tested restores and a recovery plan."),
            ("key", "Access control", "Quarterly access reviews, MFA on admin accounts and removal of former staff."),
            ("pulse", "Monitoring and response", "Alerts on failed logins and errors, and a one-page incident response plan."),
            ("shield", "Built in, not added on", "Every Apex build passes its security baseline before go-live. That is never an optional extra."),
        ],
        "examples": ["Penetration testing", "Vulnerability assessments", "Security audits", "Backup and disaster recovery", "Access control reviews", "Incident response plans"],
        "prices": [
            ("External penetration test (with a certified partner)", "Written authorisation, report, retest after fixes", "Quoted by the partner", "1–3 weeks", SPECIALIST),
            ("Vulnerability assessment or security audit", "Findings report and prioritised recommendations", "Quoted by the partner", "As agreed", SPECIALIST),
            ("Security of every system Apex builds", "Apex Security Baseline, tested with evidence", "Included in every build", "Part of delivery", NOW),
        ],
    },
}

SOLUTION_ORDER = ["software-development", "pos-systems", "websites-ecommerce", "ai-automation",
                  "data-intelligence", "cloud-hosting", "integrations-consulting", "cybersecurity"]

# Extra one-off services that apply to any project (Service Guide section 3)
GETTING_STARTED = [
    ("Discovery and Blueprint", "Requirements blueprint, risk level, estimate and timeline. Credited against the build if you go ahead.", "10,000 – 50,000", "1–2 weeks", NOW),
    ("UI/UX design only", "Wireframes, mockups, design system", "25,000 – 100,000", "1–3 weeks", NOW),
    ("Data migration and import", "Cleaning, mapping, validation, reconciliation", "20,000 – 100,000", "1–3 weeks", NOW),
    ("Logos, company profiles and brand guidelines", "Design files and usage guide", QUOTED, "As agreed", NOW),
]


def starting_price(s):
    """Lowest numeric 'from' price for a solution, or None."""
    lows = []
    for row in s["prices"]:
        price = row[2]
        if price[:1].isdigit():
            lows.append(int(price.split(" ")[0].replace(",", "")))
    return f"{min(lows):,}" if lows else None


# ---------------------------------------------------------------------------
# Hosting and maintenance plans (Service Guide 6.4, Hosting and Maintenance Agreement)
# ---------------------------------------------------------------------------
HOSTING_PACKAGES = [
    ("Starter Hosting", "Brochure and small business websites", "500 – 1,000"),
    ("Business App Hosting", "Small apps and shop POS on a shared server", "2,500 – 5,000"),
    ("Dedicated App Server", "One client: own server, PostgreSQL, backups, monitoring", "6,000 – 12,000"),
    ("High-Availability / Large", "Larger systems, separate database, staging environment", "18,000 – 35,000"),
]

MAINTENANCE_PLANS = [
    {"name": "Basic", "price": "5,000", "hours": "Up to 2 hours", "backups": "Daily, kept 7 days",
     "restore": "Twice a year", "sev1": "Within 2 business days", "cover": "Office hours",
     "best": "Websites and low-risk systems"},
    {"name": "Standard", "price": "10,000 – 15,000", "hours": "4 to 6 hours", "backups": "Daily, kept 14 days",
     "restore": "Quarterly", "sev1": "Within 24 hours", "cover": "Office hours",
     "best": "Business systems and web apps"},
    {"name": "POS Care", "price": "15,000 – 22,000", "hours": "About 8 hours", "backups": "Daily, kept 30 days",
     "restore": "Quarterly", "sev1": "Within 2 hours in trading hours", "cover": "Your trading hours, 7 days",
     "best": "Shops, restaurants and bars", "featured": True},
    {"name": "Premium", "price": "25,000 and above", "hours": "10 or more hours", "backups": "Daily, kept 30 days",
     "restore": "Monthly", "sev1": "Within 4 hours in support hours", "cover": "Office hours",
     "best": "Critical systems, quarterly security review"},
]

# Pricing page: three starting points for the most-asked-for builds
PRICE_STARTERS = [
    {"icon": "globe", "name": "Website", "short": "website", "for": "Small businesses, NGOs and schools", "price": "15,000",
     "points": ["Responsive design on every device", "Contact form with spam protection", "Basic SEO and Google Business setup", "30-day warranty after launch"],
     "slug": "websites-ecommerce"},
    {"icon": "pos", "name": "POS system", "short": "POS", "for": "Shops, restaurants, bars and pharmacies", "price": "80,000",
     "points": ["Sales, receipts, stock and reports", "M-Pesa with automatic reconciliation", "KRA eTIMS for VAT-registered shops", "Works through outages"],
     "slug": "pos-systems", "featured": True},
    {"icon": "code", "name": "Business system", "short": "software", "for": "Organisations replacing spreadsheets", "price": "150,000",
     "points": ["Roles, approvals and audit trail", "Reports with Excel and PDF export", "M-Pesa, SMS and email integrations", "Data imported from your files"],
     "slug": "software-development"},
]

ADD_ONS = [
    "Hosting and maintenance plans",
    "Data migration and import",
    "M-Pesa and card payment integration",
    "Extra staff training",
    "Independent penetration test (Level 3 systems)",
]

# ---------------------------------------------------------------------------
# Delivery process (Proposal template section 3, Pricing Guide section 7)
# ---------------------------------------------------------------------------
PROCESS = [
    ("chat", "Discover", "We listen to understand your business needs, goals and challenges."),
    ("doc", "Plan", "Every role, page, rule and integration goes into a blueprint you review and sign, with a fixed price."),
    ("pen", "Design", "You see and approve mockups of every screen before any code is written."),
    ("code", "Develop", "We build module by module and show progress on a private staging link."),
    ("shield", "Test", "Functional, calculation, device and security testing against the Apex Security Baseline."),
    ("rocket", "Deploy", "We launch smoothly, train your staff and hand over documents and credentials."),
    ("support", "Support", "Free defect fixes during the warranty, then a maintenance plan that fits your hours."),
    ("chart", "Grow", "We help you add modules, users and branches as your business grows."),
]

# Trust and security page (Security Baseline, in plain language)
SECURITY_COMMITMENTS = [
    ("lock", "Data protection", "Personal data is kept to what the system needs, encrypted in transit and backed up encrypted."),
    ("shield", "Secure development", "Every module is reviewed, scanned and tested against a written security baseline."),
    ("users", "Controlled access", "People see only what their role allows, checked on the server for every request."),
    ("pulse", "Continuous monitoring", "Uptime, errors and failed logins are monitored, with alerts to a named person."),
    ("refresh", "Reliable backups", "Daily encrypted backups copied off the server, with restore tests on a schedule."),
    ("gear", "Regular updates", "Security patches and dependency updates applied on a set schedule."),
]

STANDARDS = [
    ("shield", "Apex Security Baseline", "118 controls in 12 areas, tested with evidence"),
    ("flag", "Data Protection Act, 2019", "Built for Kenyan data protection duties"),
    ("search", "OWASP-based testing", "Scans and manual tests on every build"),
    ("card", "Card data kept off our systems", "Card entry on the gateway's hosted page"),
]

SECURITY_POINTS = [
    ("Security is a condition of delivery", "Every system is built to the Apex Security Baseline: a written set of controls for logins, permissions, data, payments, servers and backups."),
    ("Proven with evidence", "Each control is tested on staging and recorded: scan reports, permission tests, header and TLS checks and a backup restore."),
    ("No open serious findings at go-live", "Critical and High findings are fixed before launch. They are never waived."),
    ("Payments checked twice", "Totals are calculated on the server, payment callbacks are verified with the provider, and each transaction is processed once."),
    ("Your data, handled properly", "We act as data processor under the Data Protection Act, 2019. Personal data stays in Kenya unless you instruct otherwise in writing."),
    ("Honest about limits", "No software is unbreakable. We promise a defined baseline, tested and evidenced, and a maintenance plan to keep it that way."),
]

CLIENT_RESPONSIBILITIES = [
    "Turn on two-step login (MFA) for your own admin accounts.",
    "Never share passwords between staff.",
    "Remove staff who leave on the day they leave.",
    "Keep your computers and phones updated.",
]

# ---------------------------------------------------------------------------
# Why Apex, values, mission
# ---------------------------------------------------------------------------
HERO_POINTS = [
    ("rocket", "Modern technology"),
    ("shield", "Security tested to a written baseline"),
    ("support", "Dedicated support"),
    ("flag", "Built for Kenyan businesses"),
]

WHY_APEX = [
    ("doc", "Written blueprint first", "Scope, rules and acceptance criteria are agreed in writing before code, so there are no surprises later."),
    ("tag", "Fixed-scope packages", "Clear prices with VAT shown, not open-ended hourly billing."),
    ("shield", "Security you can verify", "Built to a published baseline and handed over with an evidence pack."),
    ("flag", "Kenya-ready", "M-Pesa, KRA eTIMS, SMS and the Data Protection Act are part of how we build, not add-ons."),
    ("key", "You own your work", "Your code once paid for, and your domains and accounts in your own name."),
    ("support", "Support after launch", "Warranty, then maintenance plans with stated response times, including trading-hours cover for POS."),
]

# Shown as a strip; numbers are added here only once they are real and verifiable.
PROOF_STRIP = [
    ("trophy", "Real projects", "Shown with their true status"),
    ("tag", "Clear pricing", "Fixed scope, VAT shown"),
    ("shield", "Security tested", "Evidence at every handover"),
    ("handshake", "Long-term partnership", "Hosting and support after launch"),
]

VALUES = [
    ("bulb", "Innovation", "Embrace new ideas."),
    ("scale", "Integrity", "Do what is right."),
    ("star", "Excellence", "Deliver the best."),
    ("users", "Customer partnership", "Grow together."),
]

MISSION = "To empower organisations with innovative, secure and scalable technology solutions."
VISION = "To be Africa's most trusted technology solutions partner."

HOME_PROBLEMS = [
    ("pos", "Losing track of stock and sales?", "POS and inventory systems that show what sold, what is left and what is missing.", "pos-systems"),
    ("layers", "Running the business on spreadsheets?", "Business systems with roles, approvals, audit trails and reports.", "software-development"),
    ("globe", "Hard to find or buy from online?", "Websites and online stores that load fast and take M-Pesa.", "websites-ecommerce"),
    ("plug", "Reconciling M-Pesa by hand?", "Payment integrations that confirm, record and reconcile automatically.", "integrations-consulting"),
]

# ---------------------------------------------------------------------------
# Portfolio. Real work only, true status, no invented results (copy rule 5).
# ---------------------------------------------------------------------------
WORK = [
    {
        "slug": "qt-ladies-collection",
        "title": "QT Ladies Collection",
        "category": "E-commerce",
        "filter": "web",
        "status": "MVP live",
        "image": "work-qt",
        "summary": "A modern online store for a women's clothing boutique in Ongata Rongai, Kajiado.",
        "chips": [("cart", "Online sales"), ("card", "Checkout"), ("chart", "Order admin")],
        "client": "A women's fashion boutique selling in-store, extending to online orders.",
        "challenge": "Customers browsed through photos shared on social media and ordered by message, with no catalogue, cart or price list in one place.",
        "solution": "A phased e-commerce build. Phase 1 delivered a product catalogue with prices in Kenya shillings, a cart, checkout and customer accounts. Later phases add an online payment gateway, order emails and image hosting.",
        "features": ["Product catalogue with KES pricing", "Cart and checkout", "Customer accounts", "Brand identity in the boutique's gold, cream and red", "Shop banners and print-ready graphics"],
        "tech": ["Next.js", "Vercel", "JWT authentication"],
        "visual": "store",
    },
    {
        "slug": "bar-lounge-pos",
        "title": "Bar and Lounge POS",
        "category": "POS",
        "filter": "pos",
        "status": "In development",
        "image": "work-pos",
        "summary": "A point-of-sale system for a bar and lounge, with stock, purchasing and M-Pesa.",
        "chips": [("pos", "Table orders"), ("box", "Stock"), ("chart", "Sales reports")],
        "client": "A bar and lounge that needs every drink, payment and stock movement accounted for.",
        "challenge": "Sales, stock and supplier purchases were tracked separately, making it hard to see what sold, what was left and where stock went.",
        "solution": "A Flask and PostgreSQL POS with M-Pesa STK push, inventory and purchase management, stock control and analytics, built page by page from approved designs.",
        "features": ["Sales screen and receipts", "M-Pesa STK push via Daraja", "Inventory and stock management", "Purchase management", "Sales analytics"],
        "tech": ["Python", "Flask", "PostgreSQL", "M-Pesa Daraja"],
        "visual": "store",
    },
    {
        "slug": "finance-intel",
        "title": "Finance Intel Platform",
        "category": "Finance",
        "filter": "data",
        "status": "In development",
        "image": "work-finance",
        "summary": "Company analysis and governance intelligence built on Nairobi Securities Exchange annual reports.",
        "chips": [("chart", "Market data"), ("doc", "Reports"), ("search", "Evidence")],
        "client": "An Apex product for boards, analysts and HR teams who benchmark director pay and governance.",
        "challenge": "Board and director remuneration data is buried in long PDF annual reports, in different layouts, units and scales, so benchmarking it takes weeks of manual reading.",
        "solution": "A Flask platform that imports annual report PDFs, extracts board, remuneration and financial figures with a source reference for each value, routes every import through a human review step, and builds cross-company benchmarks and narrated PDF reports.",
        "features": ["PDF import with page-level evidence for each value", "Review and approval before data is used", "Unit and currency detection per filing", "Cross-company averages and percentiles", "Narrated PDF reports per company and year", "Role-based access and rate-limited data routes"],
        "tech": ["Python", "Flask", "PostgreSQL", "pdfplumber"],
        "visual": "dashboard",
    },
    {
        "slug": "school-management-system",
        "title": "School Management System",
        "category": "Education",
        "filter": "education",
        "status": "In development",
        "image": "work-school",
        "summary": "A public website and staff portals for a secondary school, from admissions to timetables.",
        "chips": [("users", "Portals"), ("doc", "Academics"), ("chat", "Communication")],
        "client": "A secondary school in Meru County moving its records and communication online.",
        "challenge": "Admissions, fees, academics and parent communication ran on paper and separate files, with no single view of a student.",
        "solution": "A public school website plus admin, finance, communication, teacher, academics and website-manager portals, with timetable generation and transport as the next modules.",
        "features": ["Public school website", "Admin and finance portals", "Teacher and academics portals", "Parent communication", "Timetable generator (next)", "Transport module (next)"],
        "tech": ["Python", "Flask", "PostgreSQL"],
        "visual": "dashboard",
    },
    {
        "slug": "match-oracle",
        "title": "Match Oracle",
        "category": "Analytics",
        "filter": "data",
        "status": "Internal project",
        "image": "svc-data",
        "summary": "A data platform that ingests fixtures and results from an external API and runs a multi-module analysis pipeline.",
        "chips": [("plug", "API integration"), ("chart", "Dashboards"), ("pulse", "Data repair")],
        "client": "An Apex research project used to develop data-integration and analytics methods.",
        "challenge": "Working within a strict daily API call budget while keeping thousands of fixtures, results and league tables accurate and up to date.",
        "solution": "A Flask application with a cached local database, a resumable season backfill, scheduled catch-up of late results, and a pipeline of analysis modules that produces explainable, data-backed reports. Installable on phones as a web app.",
        "features": ["External API integration within a daily call budget", "Local caching and resumable backfill", "Scheduled data repair and diagnostics", "Multi-module analysis pipeline", "Installable web app (PWA)"],
        "tech": ["Python", "Flask", "SQLite", "REST API integration"],
        "visual": "pipeline",
    },
]

WORK_FILTERS = [
    ("all", "All", "grid"),
    ("web", "Websites & E-commerce", "globe"),
    ("pos", "POS Systems", "pos"),
    ("data", "Data & Analytics", "chart"),
    ("education", "Education", "school"),
]

# ---------------------------------------------------------------------------
# Industries. Two full pages in Phase 1; the rest are summarised on /industries.
# ---------------------------------------------------------------------------
INDUSTRIES = {
    "retail-hospitality": {
        "slug": "retail-hospitality",
        "title": "Retail and hospitality",
        "icon": "pos",
        "hero": "work-pos",
        "lede": "For shops, minimarts, pharmacies, restaurants, bars and lounges that need every sale, payment and item accounted for.",
        "challenges": [
            ("Stock that does not add up", "Counts take days, and losses between deliveries, sales and the shelf are hard to trace."),
            ("Cash and M-Pesa reconciliation", "End-of-day totals are checked against statements by hand."),
            ("Owner away from the counter", "No way to see today's sales or low stock from a phone."),
            ("Tax compliance", "VAT-registered businesses need eTIMS-compliant invoices for every sale."),
            ("Outages", "Internet drops and power cuts stop sales or corrupt records."),
            ("Weekend trading", "Problems happen when office-hours support is closed."),
        ],
        "solutions": ["pos-systems", "integrations-consulting", "cloud-hosting", "websites-ecommerce"],
        "modules": ["Sales screen and receipts", "Stock, suppliers and purchasing", "Tables, kitchen and bar tickets, split bills", "Shifts and cash-up", "M-Pesa STK push and reconciliation", "KRA eTIMS", "Owner phone dashboard", "Offline mode"],
        "work": ["bar-lounge-pos", "qt-ladies-collection"],
        "support_note": "POS Care covers your actual trading hours, seven days a week, with a 2-hour response to critical faults.",
    },
    "education": {
        "slug": "education",
        "title": "Education",
        "icon": "school",
        "hero": "work-school",
        "lede": "For schools that want admissions, student records, fees and parent communication in one place, with children's data properly protected.",
        "challenges": [
            ("Fee tracking", "Payments arrive through M-Pesa, bank and cash and are matched to students by hand."),
            ("Scattered records", "Admissions, class lists and results sit in separate files."),
            ("Parent communication", "Messages and fee reminders go out one by one."),
            ("Report cards", "Term reports are compiled manually at the busiest time of the year."),
            ("Protecting children's data", "Records of minors need strict access control and logging."),
            ("A website that works", "Parents need current information, downloads and contact details."),
        ],
        "solutions": ["software-development", "websites-ecommerce", "integrations-consulting", "cloud-hosting"],
        "modules": ["Admissions and student records", "Fees, M-Pesa payments and statements", "Parent portal and SMS notices", "Exams and report cards", "Staff and class management", "Timetables and transport", "School website"],
        "work": ["school-management-system"],
        "support_note": "School systems hold children's data, so they are built to Level 3 of the Apex Security Baseline: role-based views, logged access to records and approval for exports.",
    },
}

INDUSTRY_TILES = [
    ("Retail & Wholesale", "ind-retail", "retail-hospitality", "POS, stock, suppliers and branch reporting."),
    ("Hospitality", "ind-hospitality", "retail-hospitality", "Restaurant, bar and hotel POS with kitchen tickets."),
    ("Education", "ind-education", "education", "School management, fees, portals and websites."),
    ("Healthcare", "ind-healthcare", None, "Clinic administration and appointments, by consultation with enhanced security review."),
    ("Corporate Services", "ind-corporate", None, "ERP, CRM, HR and payroll, workflows and analytics."),
    ("NGOs & Institutions", "ind-ngo", None, "Membership, donor reporting, documents and websites."),
    ("Finance & Property", "ind-finance", None, "SACCO, property and tenancy systems, and governance intelligence."),
]

# ---------------------------------------------------------------------------
# Contact form choices
# ---------------------------------------------------------------------------
SERVICE_CHOICES = [("", "Choose a service")] + [(k, SOLUTIONS[k]["title"]) for k in SOLUTION_ORDER] + [("other", "Something else / not sure")]

BUDGET_CHOICES = [
    ("", "Choose a range"),
    ("under-50k", "Under KES 50,000"),
    ("50k-150k", "KES 50,000 – 150,000"),
    ("150k-300k", "KES 150,000 – 300,000"),
    ("300k-600k", "KES 300,000 – 600,000"),
    ("over-600k", "Over KES 600,000"),
    ("not-sure", "Not sure yet"),
]

FAQS = [
    ("Do your prices include VAT?", "No. All prices exclude 16% VAT. Every proposal shows the total including VAT."),
    ("Do you offer payment plans?", "Yes. Builds are paid in three stages: 50% when the Development Agreement is signed, 30% when you approve the staging system, and 20% before go-live. Work starts only after the agreement is signed."),
    ("What is included in a package?", "Each proposal offers Basic, Standard and Premium options with the scope, design rounds, training, warranty and timeline written out, so you can compare them side by side."),
    ("Can I upgrade later?", "Yes. Systems are built in modules, so you can add features, users or branches later. Each addition is quoted before work starts."),
    ("Is hosting included in the build price?", "No. Hosting and maintenance are separate monthly plans, so you only pay for the level of support you need."),
    ("Who owns the system?", "You own the custom work once it is fully paid. Apex keeps its reusable tools and components and gives you a licence to use them."),
    ("What does the warranty cover?", "Free fixes for defects against the signed acceptance criteria for 30 to 60 days after go-live, depending on the package."),
    ("What costs go to other providers?", "Domains, SMS credits, M-Pesa and card transaction fees, app store accounts and hardware are paid directly by you and kept in your name."),
]
