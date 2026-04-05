from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class CompanySize(str, Enum):
    MICRO  = "1-9 employees"
    SMALL  = "10-49 employees"
    MEDIUM = "50-249 employees"
    LARGE  = "250+ employees"


# ── Client Info ────────────────────────────────────────────────────────────────

class ClientInfo(BaseModel):
    company_name:  str = Field(..., example="Acme Ltd")
    contact_name:  str = Field(..., example="Jane Smith")
    contact_email: str = Field(..., example="jane@acme.co.uk")
    company_size:  CompanySize
    industry:      str = Field(..., example="Legal Services")


# ── Control 1: Firewalls ───────────────────────────────────────────────────────

class FirewallsControl(BaseModel):
    firewall_on_all_devices:       bool = Field(..., description="Firewall configured on all internet-connected devices")
    default_admin_password_changed: bool = Field(..., description="Default admin credentials changed on all firewalls/routers")
    unnecessary_ports_blocked:      bool = Field(..., description="Unnecessary inbound ports are blocked")
    firewall_rules_documented:      bool = Field(..., description="Firewall rules are documented and reviewed regularly")
    boundary_firewall_in_place:     bool = Field(..., description="A boundary firewall protects the network perimeter")


# ── Control 2: Secure Configuration ───────────────────────────────────────────

class SecureConfigControl(BaseModel):
    default_passwords_changed:      bool = Field(..., description="Default passwords changed on all software and devices")
    unnecessary_software_removed:   bool = Field(..., description="Unnecessary software and services are removed or disabled")
    auto_run_disabled:              bool = Field(..., description="Auto-run features are disabled")
    configuration_process_exists:   bool = Field(..., description="A formal process exists for managing system configurations")
    software_inventory_maintained:  bool = Field(..., description="An up-to-date software inventory is maintained")


# ── Control 3: Access Control ──────────────────────────────────────────────────

class AccessControlControl(BaseModel):
    unique_accounts_per_user:       bool = Field(..., description="Unique user accounts exist for each individual")
    admin_access_restricted:        bool = Field(..., description="Admin privileges are limited to those who need them")
    mfa_for_remote_access:          bool = Field(..., description="Multi-factor authentication used for remote access")
    offboarding_process_exists:     bool = Field(..., description="Access is promptly removed when staff leave")
    privileged_account_monitoring:  bool = Field(..., description="Privileged accounts are monitored and reviewed regularly")


# ── Control 4: Malware Protection ─────────────────────────────────────────────

class MalwareProtectionControl(BaseModel):
    antivirus_installed:            bool = Field(..., description="Anti-malware software installed on all devices")
    antivirus_auto_updates:         bool = Field(..., description="Anti-malware signatures update automatically")
    web_filtering_in_place:         bool = Field(..., description="Web filtering blocks access to malicious sites")
    email_scanning_active:          bool = Field(..., description="Inbound email is scanned for malicious content")
    usb_usage_controlled:           bool = Field(..., description="Removable media usage is restricted or controlled")


# ── Control 5: Patch Management ───────────────────────────────────────────────

class PatchManagementControl(BaseModel):
    auto_updates_enabled:           bool = Field(..., description="Automatic updates enabled across all software and OS")
    patches_applied_within_14_days: bool = Field(..., description="Security patches applied within 14 days of release")
    unsupported_software_removed:   bool = Field(..., description="Unsupported or end-of-life software is removed")
    asset_inventory_exists:         bool = Field(..., description="A full hardware and software asset inventory is maintained")
    patch_process_documented:       bool = Field(..., description="A documented patch management process exists")


# ── Full Assessment Request ────────────────────────────────────────────────────

class AssessmentRequest(BaseModel):
    client:             ClientInfo
    firewalls:          FirewallsControl
    secure_config:      SecureConfigControl
    access_control:     AccessControlControl
    malware_protection: MalwareProtectionControl
    patch_management:   PatchManagementControl


# ── Gap & Report Models ────────────────────────────────────────────────────────

class ControlGap(BaseModel):
    gap_title:          str
    description:        str
    remediation_steps:  list[str]
    priority:           int = Field(..., ge=1, le=5, description="1 = Critical, 5 = Low")
    ncsc_reference:     Optional[str] = None


class ControlResult(BaseModel):
    control_name:       str
    score:              int = Field(..., ge=0, le=100)
    risk_level:         RiskLevel
    passed_checks:      int
    total_checks:       int
    gaps:               list[ControlGap]
    summary:            str


class AssessmentResult(BaseModel):
    client:             ClientInfo
    overall_score:      int
    overall_risk:       RiskLevel
    cyber_essentials_ready: bool
    controls:           list[ControlResult]
    executive_summary:  str
    top_priorities:     list[str]
    estimated_effort:   str
