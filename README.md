# CyberGuard Compliance API
### AI-Powered Cyber Essentials Gap Analysis for UK SMEs
**Built by [ashcybersec](https://ashcybersec.github.io) | Powered by Claude AI**

---

## What It Does
CyberGuard is an agentic AI compliance service that:
- Accepts a Cyber Essentials self-assessment questionnaire via API
- Analyses responses against all 5 NCSC Cyber Essentials controls
- Returns a structured gap analysis with risk scores and remediation steps
- Generates a branded, downloadable PDF report

All gap analysis is performed by a Claude AI agent with deep knowledge of NCSC requirements and UK GDPR context.

---

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11+) |
| AI Engine | Claude Haiku (Anthropic API) |
| PDF Reports | ReportLab |
| Deployment | Hetzner CX22 VPS / Docker |

---

## Quick Start

### 1. Clone & Set Up
```bash
git clone https://github.com/ashcybersec/cyberguard-compliance.git
cd cyberguard-compliance
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test It
Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## API Endpoints

### `POST /api/v1/assess`
Returns JSON gap analysis.

### `POST /api/v1/assess/report`
Returns a downloadable PDF gap analysis report.

### `GET /api/v1/health`
Health check.

---

## Example Request
```json
{
  "client": {
    "company_name": "Acme Ltd",
    "contact_name": "Jane Smith",
    "contact_email": "jane@acme.co.uk",
    "company_size": "10-49 employees",
    "industry": "Legal Services"
  },
  "firewalls": {
    "firewall_on_all_devices": true,
    "default_admin_password_changed": false,
    "unnecessary_ports_blocked": true,
    "firewall_rules_documented": false,
    "boundary_firewall_in_place": true
  },
  "secure_config": {
    "default_passwords_changed": false,
    "unnecessary_software_removed": true,
    "auto_run_disabled": true,
    "configuration_process_exists": false,
    "software_inventory_maintained": false
  },
  "access_control": {
    "unique_accounts_per_user": true,
    "admin_access_restricted": true,
    "mfa_for_remote_access": false,
    "offboarding_process_exists": false,
    "privileged_account_monitoring": false
  },
  "malware_protection": {
    "antivirus_installed": true,
    "antivirus_auto_updates": true,
    "web_filtering_in_place": false,
    "email_scanning_active": false,
    "usb_usage_controlled": false
  },
  "patch_management": {
    "auto_updates_enabled": true,
    "patches_applied_within_14_days": false,
    "unsupported_software_removed": true,
    "asset_inventory_exists": false,
    "patch_process_documented": false
  }
}
```

---

## Deployment (Hetzner CX22)
```bash
# Install Docker on Ubuntu 24.04
curl -fsSL https://get.docker.com | sh

# Build and run
docker build -t cyberguard .
docker run -d -p 8000:8000 --env-file .env cyberguard

# Set up Nginx reverse proxy + SSL with Certbot
```

---

## Pricing Model (SaaS)
| Tier | Price | Offering |
|---|---|---|
| One-time Assessment | £99 | Full gap report PDF |
| Basic Monitoring | £199/month | Quarterly reassessment + alerts |
| Pro Monitoring | £399/month | Monthly + SLA support |

---

## Roadmap
- [ ] React frontend with guided questionnaire
- [ ] Stripe payment integration
- [ ] Email PDF delivery on payment
- [ ] Client dashboard with historical trend tracking
- [ ] Cyber Essentials Plus evidence pack generator
- [ ] GDPR Article 32 readiness module
- [ ] Automated follow-up email sequences

---

## Author
**Ashfaq Ahmed** | ashcybersec@proton.me | [ashcybersec.github.io](https://ashcybersec.github.io)
