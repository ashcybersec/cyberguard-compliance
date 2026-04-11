CYBER_ESSENTIALS_SYSTEM_PROMPT = """
You are CyberGuard, an expert UK cybersecurity compliance analyst specialising in the 
NCSC Cyber Essentials scheme (v3.3, April 2026 — "Danzell" release). You analyse 
organisations' security posture against the five CE controls and produce precise, 
actionable gap analysis reports for UK SMEs.

## Cyber Essentials v3.3 Key Changes (April 2026)
- MFA is now MANDATORY for ALL cloud services where available — failure is an automatic CE fail
- Critical patches must be applied within 14 days — failure is an automatic CE fail  
- Cloud services CANNOT be excluded from scope
- BYOD devices accessing company data are now in scope
- Firmware on routers/firewalls must be kept updated
- Windows 10 reached end-of-life October 2025 — any device running it will automatically fail

## Auto-Fail Conditions (CE v3.3)
The following AUTOMATICALLY fail a Cyber Essentials assessment:
1. No MFA on any cloud service where it is available (M365, Google Workspace, etc.)
2. Critical patches not applied within 14 days
3. Unsupported OS in use (Windows 7, Windows 8, Windows 10 post Oct 2025, macOS > 3 years old)
4. No boundary firewall
5. No anti-malware on devices

## Scoring Logic
- Each control is scored 0-100 based on answered questions
- Weight the 5 core questions equally, bonus for additional questions answered correctly
- Risk Level: 80-100 = LOW, 60-79 = MEDIUM, 40-59 = HIGH, 0-39 = CRITICAL
- cyber_essentials_ready = true ONLY if ALL controls >= 80 AND no auto-fail conditions

## Output Format
Respond ONLY with valid JSON — no preamble, no markdown, no explanation outside JSON.

{
  "overall_score": <integer 0-100>,
  "overall_risk": <"low"|"medium"|"high"|"critical">,
  "cyber_essentials_ready": <boolean>,
  "auto_fail_items": ["<description of any auto-fail condition found>"],
  "certification_verdict": "<Ready for Certification|Nearly Ready (1-4 weeks)|Not Ready (1-3 months)>",
  "controls": [
    {
      "control_name": "<name>",
      "score": <integer 0-100>,
      "risk_level": <"low"|"medium"|"high"|"critical">,
      "passed_checks": <integer>,
      "total_checks": <integer>,
      "gaps": [
        {
          "gap_title": "<short title>",
          "description": "<what is wrong and why it matters>",
          "remediation_steps": ["<step 1>", "<step 2>", "<step 3>"],
          "priority": <1-5 where 1=critical, 5=low>,
          "ncsc_reference": "<CE v3.3 section reference>"
        }
      ],
      "summary": "<2-3 sentence plain-English summary>"
    }
  ],
  "executive_summary": "<3-4 sentence non-technical summary for a business director. Include overall score, main risks, and whether certification is achievable>",
  "top_priorities": ["<specific action 1>", "<specific action 2>", "<specific action 3>", "<action 4>", "<action 5>"],
  "estimated_effort": "<realistic estimate e.g. '2-4 weeks with internal IT resource'>"
}

## UK Context
- Reference NCSC Cyber Essentials v3.3 (April 2026) requirements throughout
- Note GDPR Article 32 implications for access control and data protection gaps
- CE certification required for UK government contracts over £25k
- Basic CE self-assessment costs from £320+VAT via IASME-licensed bodies
- CE+ (with independent assessment) from £1,500+VAT — required for some contracts
- NCSC provides free Cyber Essentials cyber liability insurance for UK organisations under £20M turnover
- Be specific to the organisation's industry where sector-specific risks apply
""".strip()


def build_assessment_prompt(request_data: dict) -> str:
    client = request_data["client"]
    fw     = request_data["firewalls"]
    sc     = request_data["secure_config"]
    ac     = request_data["access_control"]
    mp     = request_data["malware_protection"]
    pm     = request_data["patch_management"]

    cloud_services = client.get("cloud_services") or []
    cloud_str = ", ".join(cloud_services) if cloud_services else "None specified"

    return f"""
Analyse this Cyber Essentials v3.3 self-assessment for {client["company_name"]}.

## Organisation Profile
- Company:         {client["company_name"]}
- Industry:        {client["industry"]}
- Size:            {client["company_size"]}
- Devices in scope: {client.get("device_count", "Not specified")}
- Cloud services:  {cloud_str}
- BYOD in use:     {client.get("has_byod", "Not specified")}
- Remote workers:  {client.get("remote_workers", "Not specified")}
- Contact:         {client["contact_name"]} ({client["contact_email"]})

## CONTROL 1 — Firewalls
Core questions:
- Firewall on all internet-connected devices: {fw["firewall_on_all_devices"]}
- Default admin passwords changed on routers/firewalls: {fw["default_admin_password_changed"]}
- Unnecessary inbound ports blocked: {fw["unnecessary_ports_blocked"]}
- Firewall rules documented and reviewed: {fw["firewall_rules_documented"]}
- Boundary firewall in place: {fw["boundary_firewall_in_place"]}

Additional (CE v3.3):
- Software firewall enabled on all laptops/desktops: {fw.get("software_firewall_on_devices", "Not answered")}
- Cloud security groups configured (AWS/Azure/GCP): {fw.get("cloud_firewall_configured", "Not answered")}
- Remote workers use company VPN: {fw.get("remote_vpn", "Not answered")}

## CONTROL 2 — Secure Configuration
Core questions:
- Default passwords changed on all systems: {sc["default_passwords_changed"]}
- Unnecessary software removed/disabled: {sc["unnecessary_software_removed"]}
- Auto-run disabled: {sc["auto_run_disabled"]}
- Configuration management process exists: {sc["configuration_process_exists"]}
- Software inventory maintained: {sc["software_inventory_maintained"]}

Additional (CE v3.3):
- Screen auto-lock enabled: {sc.get("screen_lock_enabled", "Not answered")}
- BYOD policy enforced: {sc.get("byod_policy_enforced", "Not answered")}
- Cloud security defaults enabled (M365/Google): {sc.get("cloud_security_defaults", "Not answered")}

## CONTROL 3 — User Access Control
Core questions:
- Unique accounts per user (no shared logins): {ac["unique_accounts_per_user"]}
- Admin access restricted to those who need it: {ac["admin_access_restricted"]}
- MFA enforced for remote access: {ac["mfa_for_remote_access"]}
- Offboarding process — access removed on day of leaving: {ac["offboarding_process_exists"]}
- Privileged accounts monitored: {ac["privileged_account_monitoring"]}

Additional (CE v3.3 — MFA now mandatory on ALL cloud services):
- MFA on M365/Google Workspace for ALL users: {ac.get("mfa_on_cloud_services", "Not answered")}
- MFA on other cloud services (Xero, CRM, etc.): {ac.get("mfa_on_other_cloud", "Not answered")}
- Separate admin accounts for IT tasks: {ac.get("separate_admin_accounts", "Not answered")}
- Password policy (min 8 chars): {ac.get("password_policy_enforced", "Not answered")}
- Third-party supplier accounts reviewed: {ac.get("third_party_accounts_reviewed", "Not answered")}

## CONTROL 4 — Malware Protection
Core questions:
- Anti-malware installed on all devices: {mp["antivirus_installed"]}
- AV signatures auto-update (daily/real-time): {mp["antivirus_auto_updates"]}
- Web filtering in place: {mp["web_filtering_in_place"]}
- Email scanning active: {mp["email_scanning_active"]}
- Removable media controlled: {mp["usb_usage_controlled"]}

Additional (CE v3.3):
- AV centrally managed (not user-controlled): {mp.get("av_centrally_managed", "Not answered")}
- Mobile devices protected (AV or MDM): {mp.get("mobile_devices_protected", "Not answered")}
- Cloud storage scanned for malware: {mp.get("cloud_storage_scanned", "Not answered")}

## CONTROL 5 — Security Update Management
Core questions:
- Automatic updates enabled: {pm["auto_updates_enabled"]}
- Critical patches applied within 14 days: {pm["patches_applied_within_14_days"]}
- Unsupported/EOL software removed: {pm["unsupported_software_removed"]}
- Asset inventory exists: {pm["asset_inventory_exists"]}
- Patch process documented: {pm["patch_process_documented"]}

Additional (CE v3.3):
- Router/firewall firmware updated regularly: {pm.get("firmware_updated", "Not answered")}
- Mobile devices kept up to date: {pm.get("mobile_devices_patched", "Not answered")}
- Third-party apps (browsers, Office, Adobe) patched: {pm.get("third_party_apps_patched", "Not answered")}
- No unsupported OS confirmed (no Win7/8/10-EOL): {pm.get("unsupported_os_confirmed", "Not answered")}

Now produce the full CE v3.3 gap analysis JSON. Check for auto-fail conditions first.
For the industry "{client["industry"]}" include any sector-specific risks or regulatory 
implications (e.g. SRA for legal, CQC for healthcare, FCA for financial services).
""".strip()
