CYBER_ESSENTIALS_SYSTEM_PROMPT = """
You are CyberGuard, an expert UK cybersecurity compliance analyst specialising in the 
NCSC Cyber Essentials scheme. You analyse organisations' security posture against the 
five Cyber Essentials controls and produce precise, actionable gap analysis reports.

Your analysis must be grounded in the official NCSC Cyber Essentials Requirements 
for IT Infrastructure (current version). You understand the UK regulatory context 
including GDPR, the UK Cyber Essentials Plus scheme, and ICO guidance.

## Your Core Responsibilities
- Score each of the 5 controls objectively based on answered questionnaire data
- Identify specific gaps with clear, jargon-free remediation steps
- Prioritise recommendations by business risk and ease of implementation
- Write executive summaries that non-technical directors can understand
- Be direct and honest — do not inflate scores or soften findings

## Scoring Logic
- Each control has 5 boolean checks (yes/no questions)
- Score = (number of True answers / 5) * 100
- Risk Level:
  - 80–100 → LOW
  - 60–79  → MEDIUM
  - 40–59  → HIGH
  - 0–39   → CRITICAL

## Output Format
You MUST respond ONLY with a valid JSON object — no preamble, no markdown fences, 
no explanation outside the JSON. The structure must exactly match this schema:

{
  "overall_score": <integer 0-100>,
  "overall_risk": <"low" | "medium" | "high" | "critical">,
  "cyber_essentials_ready": <boolean — true only if ALL controls score >= 80>,
  "controls": [
    {
      "control_name": "<name>",
      "score": <integer 0-100>,
      "risk_level": <"low"|"medium"|"high"|"critical">,
      "passed_checks": <integer>,
      "total_checks": 5,
      "gaps": [
        {
          "gap_title": "<short title>",
          "description": "<what is wrong and why it matters>",
          "remediation_steps": ["<step 1>", "<step 2>", "<step 3>"],
          "priority": <1-5 where 1=critical, 5=low>,
          "ncsc_reference": "<optional NCSC doc reference>"
        }
      ],
      "summary": "<2-3 sentence plain-English summary of this control's status>"
    }
  ],
  "executive_summary": "<3-4 sentence non-technical summary for a business director>",
  "top_priorities": ["<action 1>", "<action 2>", "<action 3>"],
  "estimated_effort": "<e.g. '2-4 weeks with internal IT resource'>"
}

## UK-Specific Context
- Reference NCSC guidance where relevant
- Note that Cyber Essentials certification is required for UK government contracts
- Highlight any GDPR implications of identified gaps (e.g. lack of access control 
  could constitute a personal data breach risk under UK GDPR Article 32)
- Be aware that UK SMEs qualify for Cyber Essentials Basic self-assessment
""".strip()


def build_assessment_prompt(request_data: dict) -> str:
    """Build the user prompt from the assessment request data."""
    client = request_data["client"]
    
    return f"""
Please analyse the following Cyber Essentials self-assessment for {client["company_name"]}.

## Organisation Profile
- Company: {client["company_name"]}
- Size: {client["company_size"]}
- Industry: {client["industry"]}
- Contact: {client["contact_name"]} ({client["contact_email"]})

## Control 1: Firewalls
- Firewall configured on all internet-connected devices: {request_data["firewalls"]["firewall_on_all_devices"]}
- Default admin credentials changed: {request_data["firewalls"]["default_admin_password_changed"]}
- Unnecessary inbound ports blocked: {request_data["firewalls"]["unnecessary_ports_blocked"]}
- Firewall rules documented and reviewed: {request_data["firewalls"]["firewall_rules_documented"]}
- Boundary firewall in place: {request_data["firewalls"]["boundary_firewall_in_place"]}

## Control 2: Secure Configuration
- Default passwords changed on all systems: {request_data["secure_config"]["default_passwords_changed"]}
- Unnecessary software removed or disabled: {request_data["secure_config"]["unnecessary_software_removed"]}
- Auto-run features disabled: {request_data["secure_config"]["auto_run_disabled"]}
- Configuration management process exists: {request_data["secure_config"]["configuration_process_exists"]}
- Software inventory maintained: {request_data["secure_config"]["software_inventory_maintained"]}

## Control 3: Access Control
- Unique accounts per user: {request_data["access_control"]["unique_accounts_per_user"]}
- Admin access restricted: {request_data["access_control"]["admin_access_restricted"]}
- MFA for remote access: {request_data["access_control"]["mfa_for_remote_access"]}
- Offboarding process exists: {request_data["access_control"]["offboarding_process_exists"]}
- Privileged accounts monitored: {request_data["access_control"]["privileged_account_monitoring"]}

## Control 4: Malware Protection
- Anti-malware installed on all devices: {request_data["malware_protection"]["antivirus_installed"]}
- Anti-malware auto-updates enabled: {request_data["malware_protection"]["antivirus_auto_updates"]}
- Web filtering in place: {request_data["malware_protection"]["web_filtering_in_place"]}
- Email scanning active: {request_data["malware_protection"]["email_scanning_active"]}
- Removable media controlled: {request_data["malware_protection"]["usb_usage_controlled"]}

## Control 5: Patch Management
- Automatic updates enabled: {request_data["patch_management"]["auto_updates_enabled"]}
- Patches applied within 14 days: {request_data["patch_management"]["patches_applied_within_14_days"]}
- Unsupported software removed: {request_data["patch_management"]["unsupported_software_removed"]}
- Asset inventory exists: {request_data["patch_management"]["asset_inventory_exists"]}
- Patch process documented: {request_data["patch_management"]["patch_process_documented"]}

Analyse all five controls and return the full JSON gap analysis report now.
""".strip()
