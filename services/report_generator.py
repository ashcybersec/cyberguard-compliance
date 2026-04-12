import os
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable
from models.questionnaire import AssessmentResult, RiskLevel


# ── Brand Colours ──────────────────────────────────────────────────────────────
BRAND_DARK    = colors.HexColor("#0D1B2A")
BRAND_NAVY    = colors.HexColor("#0a0a0f")
BRAND_ACCENT  = colors.HexColor("#00C2CB")
BRAND_LIGHT   = colors.HexColor("#F0F4F8")
BRAND_MID     = colors.HexColor("#E8EDF2")
RED           = colors.HexColor("#E63946")
RED_BG        = colors.HexColor("#FFF0F0")
AMBER         = colors.HexColor("#F4A261")
AMBER_BG      = colors.HexColor("#FFF8F0")
GREEN         = colors.HexColor("#2A9D8F")
GREEN_BG      = colors.HexColor("#F0FAF9")
ORANGE        = colors.HexColor("#E76F51")
WHITE         = colors.white
LIGHT_GREY    = colors.HexColor("#666666")
DARK_GREY     = colors.HexColor("#333333")

RISK_COLOURS = {
    RiskLevel.LOW:      GREEN,
    RiskLevel.MEDIUM:   AMBER,
    RiskLevel.HIGH:     ORANGE,
    RiskLevel.CRITICAL: RED,
}

RISK_BG = {
    RiskLevel.LOW:      GREEN_BG,
    RiskLevel.MEDIUM:   AMBER_BG,
    RiskLevel.HIGH:     AMBER_BG,
    RiskLevel.CRITICAL: RED_BG,
}

RISK_LABELS = {
    RiskLevel.LOW:      "LOW RISK",
    RiskLevel.MEDIUM:   "MEDIUM RISK",
    RiskLevel.HIGH:     "HIGH RISK",
    RiskLevel.CRITICAL: "CRITICAL RISK",
}


class ReportGenerator:
    """Generates professional PDF compliance gap reports."""

    OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "/tmp/reports")

    def __init__(self):
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def generate(self, result: AssessmentResult) -> str:
        filename = f"{self.OUTPUT_DIR}/cyberguard_{uuid.uuid4().hex[:8]}.pdf"
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            topMargin=1.8 * cm,
            bottomMargin=2 * cm,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
        )
        styles = self._build_styles()
        story  = []

        story += self._cover(result, styles)
        story.append(PageBreak())

        story += self._executive_summary(result, styles)
        story.append(Spacer(1, 0.4 * cm))

        story += self._auto_fail_section(result, styles)

        story += self._score_dashboard(result, styles)
        story.append(Spacer(1, 0.4 * cm))

        story += self._certification_verdict(result, styles)
        story.append(Spacer(1, 0.4 * cm))

        story += self._top_priorities(result, styles)
        story.append(PageBreak())

        for ctrl in result.controls:
            story += self._control_section(ctrl, styles)
            story.append(Spacer(1, 0.3 * cm))

        story += self._next_steps(result, styles)
        story.append(Spacer(1, 0.5 * cm))
        story += self._about_ce(styles)

        story.append(Spacer(1, 1 * cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_ACCENT))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            f"CyberGuard Essentials by Corvaxis Ltd  ·  ceready.co.uk  ·  "
            f"Aligned to NCSC Cyber Essentials v3.3 (April 2026)  ·  "
            f"Generated {datetime.now().strftime('%d %B %Y')}",
            styles["footer"]
        ))

        doc.build(story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return filename

    def _header_footer(self, canvas, doc):
        canvas.saveState()
        # Top bar
        canvas.setFillColor(BRAND_DARK)
        canvas.rect(0, A4[1] - 1 * cm, A4[0], 1 * cm, fill=1, stroke=0)
        canvas.setFillColor(BRAND_ACCENT)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(2 * cm, A4[1] - 0.65 * cm, "CYBERGUARD ESSENTIALS")
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 0.65 * cm, "CYBER ESSENTIALS GAP ANALYSIS REPORT")
        # Page number
        canvas.setFillColor(LIGHT_GREY)
        canvas.setFont("Helvetica", 7)
        canvas.drawCentredString(A4[0] / 2, 1 * cm, f"Page {doc.page}")
        canvas.restoreState()

    # ── Section Builders ───────────────────────────────────────────────────────

    def _cover(self, result: AssessmentResult, styles: dict) -> list:
        risk_colour = RISK_COLOURS[result.overall_risk]
        risk_label  = RISK_LABELS[result.overall_risk]
        report_id   = f"CGE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        elements = [
            Spacer(1, 1.5 * cm),
            # Logo area
            Table([[
                Paragraph("CyberGuard", styles["brand"]),
                Paragraph("ESSENTIALS", styles["brand_tag"]),
            ]], colWidths=[10 * cm, 5 * cm]),
            Spacer(1, 0.3 * cm),
            HRFlowable(width="100%", thickness=3, color=BRAND_ACCENT, spaceAfter=30),
            Spacer(1, 0.8 * cm),
            Paragraph("CYBER ESSENTIALS GAP ANALYSIS REPORT", styles["report_type"]),
            Paragraph("NCSC Cyber Essentials v3.3 (April 2026)", styles["report_standard"]),
            Spacer(1, 1.2 * cm),
            Paragraph(result.client.company_name, styles["company_name"]),
            Spacer(1, 0.2 * cm),
            Paragraph(f"{result.client.industry}  ·  {result.client.company_size}", styles["company_meta"]),
            Spacer(1, 0.5 * cm),
            Table([[
                Paragraph(f"Prepared for:", styles["meta_label"]),
                Paragraph(result.client.contact_name, styles["meta_value"]),
            ],[
                Paragraph("Date:", styles["meta_label"]),
                Paragraph(datetime.now().strftime('%d %B %Y'), styles["meta_value"]),
            ],[
                Paragraph("Report ID:", styles["meta_label"]),
                Paragraph(report_id, styles["meta_value"]),
            ]], colWidths=[4 * cm, 11 * cm]),
            Spacer(1, 1.5 * cm),
            # Score card
            Table([[
                Table([[
                    Paragraph("OVERALL SCORE", styles["score_label"]),
                    Paragraph(f"{result.overall_score}", styles["score_number"]),
                    Paragraph("out of 100", styles["score_sub"]),
                ]], colWidths=[5 * cm]),
                Table([[
                    Paragraph("RISK LEVEL", styles["score_label"]),
                    Paragraph(risk_label, styles["risk_value"]),
                    Paragraph(" ", styles["score_sub"]),
                ]], colWidths=[5 * cm]),
                Table([[
                    Paragraph("CE STATUS", styles["score_label"]),
                    Paragraph(
                        "READY" if result.cyber_essentials_ready else "NOT READY",
                        styles["ce_ready"] if result.cyber_essentials_ready else styles["ce_not_ready"]
                    ),
                    Paragraph(" ", styles["score_sub"]),
                ]], colWidths=[5 * cm]),
            ]], colWidths=[5.2 * cm, 5.2 * cm, 5.2 * cm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), BRAND_DARK),
                ("BACKGROUND", (1, 0), (1, 0), risk_colour),
                ("BACKGROUND", (2, 0), (2, 0), GREEN if result.cyber_essentials_ready else RED),
                ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
                ("ROWHEIGHT",  (0, 0), (-1, -1), 2.5 * cm),
                ("LEFTPADDING",  (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])),
            Spacer(1, 0.5 * cm),
            Paragraph(
                "CONFIDENTIAL — Prepared exclusively for " + result.client.company_name,
                styles["confidential"]
            ),
        ]
        return elements

    def _executive_summary(self, result: AssessmentResult, styles: dict) -> list:
        return [
            Paragraph("Executive Summary", styles["section_heading"]),
            HRFlowable(width="100%", thickness=1.5, color=BRAND_ACCENT, spaceAfter=10),
            Paragraph(result.executive_summary, styles["body_justify"]),
        ]

    def _auto_fail_section(self, result: AssessmentResult, styles: dict) -> list:
        auto_fails = getattr(result, 'auto_fail_items', []) or []
        if not auto_fails:
            return []

        elements = [
            Spacer(1, 0.3 * cm),
            Table([[
                Paragraph("⛔  CERTIFICATION BLOCKERS IDENTIFIED", styles["alert_heading"]),
            ]], colWidths=[15.6 * cm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), RED),
                ("TEXTCOLOR",  (0, 0), (-1, -1), WHITE),
                ("ROWHEIGHT",  (0, 0), (-1, -1), 0.8 * cm),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ])),
        ]
        for fail in auto_fails:
            elements.append(Table([[
                Paragraph(f"✗  {fail}", styles["alert_item"]),
            ]], colWidths=[15.6 * cm],
            style=TableStyle([
                ("BACKGROUND",  (0, 0), (-1, -1), RED_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING",  (0, 0), (-1, -1), 6),
                ("LINEBELOW",   (0, 0), (-1, -1), 0.5, colors.HexColor("#FFD0D0")),
            ])))
        elements.append(Spacer(1, 0.4 * cm))
        return elements

    def _score_dashboard(self, result: AssessmentResult, styles: dict) -> list:
        elements = [
            Paragraph("Control Scores at a Glance", styles["section_heading"]),
            HRFlowable(width="100%", thickness=1.5, color=BRAND_ACCENT, spaceAfter=10),
        ]

        header = [
            Paragraph("Control", styles["table_header"]),
            Paragraph("Score", styles["table_header"]),
            Paragraph("Risk", styles["table_header"]),
            Paragraph("Gaps Found", styles["table_header"]),
            Paragraph("Checks Passed", styles["table_header"]),
        ]
        rows = [header]
        for ctrl in result.controls:
            rc    = RISK_COLOURS[ctrl.risk_level]
            label = RISK_LABELS[ctrl.risk_level]
            rows.append([
                Paragraph(ctrl.control_name, styles["table_cell"]),
                Paragraph(f"{ctrl.score}/100", styles["table_cell_center"]),
                Paragraph(label, styles["table_cell_center"]),
                Paragraph(str(len(ctrl.gaps)), styles["table_cell_center"]),
                Paragraph(f"{ctrl.passed_checks}/{ctrl.total_checks}", styles["table_cell_center"]),
            ])

        tbl = Table(rows, colWidths=[6.5 * cm, 2 * cm, 3 * cm, 2 * cm, 2.5 * cm])
        ts  = TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  BRAND_DARK),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 9),
            ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("ROWHEIGHT",   (0, 0), (-1, -1), 0.75 * cm),
            ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_LIGHT, WHITE]),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ])
        # Colour code risk column
        for i, ctrl in enumerate(result.controls, start=1):
            rc = RISK_COLOURS[ctrl.risk_level]
            ts.add("TEXTCOLOR",  (2, i), (2, i), rc)
            ts.add("FONTNAME",   (2, i), (2, i), "Helvetica-Bold")
            # Colour score column by risk
            score_colour = rc
            ts.add("TEXTCOLOR",  (1, i), (1, i), score_colour)
            ts.add("FONTNAME",   (1, i), (1, i), "Helvetica-Bold")

        tbl.setStyle(ts)
        elements.append(tbl)
        return elements

    def _certification_verdict(self, result: AssessmentResult, styles: dict) -> list:
        verdict = getattr(result, 'certification_verdict', None)
        if not verdict:
            verdict = (
                "Ready for Certification" if result.cyber_essentials_ready
                else "Not Ready — Remediation Required"
            )
        colour = GREEN if result.cyber_essentials_ready else RED
        bg     = GREEN_BG if result.cyber_essentials_ready else RED_BG
        icon   = "✅" if result.cyber_essentials_ready else "⚠️"

        return [
            Table([[
                Paragraph(f"{icon}  Certification Verdict: {verdict}", styles["verdict_text"]),
            ]], colWidths=[15.6 * cm],
            style=TableStyle([
                ("BACKGROUND",   (0, 0), (-1, -1), bg),
                ("TEXTCOLOR",    (0, 0), (-1, -1), colour),
                ("LEFTPADDING",  (0, 0), (-1, -1), 12),
                ("TOPPADDING",   (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
                ("LINEAFTER",    (0, 0), (0, -1),  4, colour),
            ])),
        ]

    def _top_priorities(self, result: AssessmentResult, styles: dict) -> list:
        elements = [
            Spacer(1, 0.3 * cm),
            Paragraph("Top Remediation Priorities", styles["section_heading"]),
            HRFlowable(width="100%", thickness=1.5, color=BRAND_ACCENT, spaceAfter=6),
            Paragraph(
                f"Estimated effort to achieve CE readiness: {result.estimated_effort}",
                styles["italic"]
            ),
            Spacer(1, 0.2 * cm),
        ]
        priority_colours = [RED, RED, ORANGE, AMBER, GREEN]
        for i, p in enumerate(result.top_priorities, 1):
            colour = priority_colours[min(i - 1, 4)]
            elements.append(KeepTogether([
                Table([[
                    Paragraph(str(i), styles["priority_num"]),
                    Paragraph(p, styles["priority_text"]),
                ]], colWidths=[0.8 * cm, 14.6 * cm],
                style=TableStyle([
                    ("BACKGROUND",   (0, 0), (0, 0), colour),
                    ("TEXTCOLOR",    (0, 0), (0, 0), WHITE),
                    ("ALIGN",        (0, 0), (0, 0), "CENTER"),
                    ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING",  (1, 0), (1, 0), 8),
                    ("TOPPADDING",   (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
                    ("LINEBELOW",    (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
                ])),
            ]))
        return elements

    def _control_section(self, ctrl, styles: dict) -> list:
        rc    = RISK_COLOURS[ctrl.risk_level]
        label = RISK_LABELS[ctrl.risk_level]

        elements = [KeepTogether([
            Table([[
                Paragraph(ctrl.control_name, styles["control_heading"]),
                Paragraph(label, styles["control_risk_badge"]),
            ]], colWidths=[12 * cm, 3.6 * cm],
            style=TableStyle([
                ("BACKGROUND",   (0, 0), (0, 0), BRAND_DARK),
                ("BACKGROUND",   (1, 0), (1, 0), rc),
                ("TEXTCOLOR",    (0, 0), (-1, -1), WHITE),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN",        (1, 0), (1, 0), "CENTER"),
                ("LEFTPADDING",  (0, 0), (0, 0), 10),
                ("ROWHEIGHT",    (0, 0), (-1, -1), 0.8 * cm),
            ])),
            Spacer(1, 0.15 * cm),
            Table([[
                Paragraph(f"Score: {ctrl.score}/100", styles["ctrl_meta"]),
                Paragraph(f"Passed: {ctrl.passed_checks}/{ctrl.total_checks} checks", styles["ctrl_meta"]),
                Paragraph(f"Gaps: {len(ctrl.gaps)}", styles["ctrl_meta"]),
            ]], colWidths=[5 * cm, 5 * cm, 5.6 * cm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BRAND_MID),
                ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
                ("LEFTPADDING",(0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ])),
            Spacer(1, 0.15 * cm),
            Paragraph(ctrl.summary, styles["body_justify"]),
        ])]

        if not ctrl.gaps:
            elements.append(Table([[
                Paragraph("✅  All checks passed for this control. No remediation required.", styles["pass_note"]),
            ]], colWidths=[15.6 * cm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_BG),
                ("LEFTPADDING",(0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ])))
        else:
            for gap in sorted(ctrl.gaps, key=lambda g: g.priority):
                priority_labels = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "LOW", 5: "INFO"}
                p_label  = priority_labels.get(gap.priority, "LOW")
                p_colour = [RED, RED, ORANGE, AMBER, GREEN][min(gap.priority - 1, 4)]
                gap_bg   = RISK_BG.get(
                    [RiskLevel.CRITICAL, RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW][min(gap.priority - 1, 4)],
                    AMBER_BG
                )
                elements.append(KeepTogether([
                    Spacer(1, 0.15 * cm),
                    Table([[
                        Paragraph(f"P{gap.priority} — {p_label}", styles["gap_priority"]),
                        Paragraph(gap.gap_title, styles["gap_title"]),
                    ]], colWidths=[2.5 * cm, 13.1 * cm],
                    style=TableStyle([
                        ("BACKGROUND",   (0, 0), (0, 0), p_colour),
                        ("BACKGROUND",   (1, 0), (1, 0), gap_bg),
                        ("TEXTCOLOR",    (0, 0), (0, 0), WHITE),
                        ("TEXTCOLOR",    (1, 0), (1, 0), DARK_GREY),
                        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN",        (0, 0), (0, 0), "CENTER"),
                        ("LEFTPADDING",  (1, 0), (1, 0), 8),
                        ("ROWHEIGHT",    (0, 0), (-1, -1), 0.7 * cm),
                    ])),
                    Paragraph(gap.description, styles["gap_body"]),
                    Paragraph("Remediation Steps:", styles["remediation_header"]),
                    *[Paragraph(f"→  {step}", styles["remediation_step"]) for step in gap.remediation_steps],
                    *([Paragraph(f"Reference: {gap.ncsc_reference}", styles["ncsc_ref"])] if gap.ncsc_reference else []),
                ]))
        return elements

    def _next_steps(self, result: AssessmentResult, styles: dict) -> list:
        return [
            PageBreak(),
            Paragraph("Next Steps — Getting CE Certified", styles["section_heading"]),
            HRFlowable(width="100%", thickness=1.5, color=BRAND_ACCENT, spaceAfter=10),
            Paragraph(
                "Once you have addressed the gaps identified in this report, follow these steps "
                "to achieve your Cyber Essentials certification:",
                styles["body"]
            ),
            Spacer(1, 0.2 * cm),
            *[Paragraph(step, styles["step_item"]) for step in [
                "1.  Remediate all identified gaps, starting with CRITICAL and HIGH priority items.",
                "2.  Complete the Cyber Essentials self-assessment questionnaire on the IASME portal at iasme.co.uk.",
                "3.  Submit your completed questionnaire to an IASME-licensed certification body.",
                "4.  Basic Cyber Essentials self-assessment costs from £320+VAT.",
                "5.  Upon successful assessment, receive your NCSC-backed CE certificate.",
                "6.  Benefit from free cyber liability insurance (organisations under £20M turnover).",
            ]],
        ]

    def _about_ce(self, styles: dict) -> list:
        return [
            Spacer(1, 0.3 * cm),
            Table([[
                Paragraph("About Cyber Essentials", styles["info_heading"]),
            ],[
                Paragraph(
                    "Cyber Essentials is an NCSC-backed UK government scheme that helps organisations "
                    "protect against the most common cyber threats. Certification is required for all "
                    "UK government contracts involving personal data or sensitive information. "
                    "The scheme covers five technical controls: Firewalls, Secure Configuration, "
                    "User Access Control, Malware Protection, and Security Update Management. "
                    "Certification is available at two levels: Cyber Essentials (self-assessment) and "
                    "Cyber Essentials Plus (independent technical verification).",
                    styles["info_body"]
                ),
            ]], colWidths=[15.6 * cm],
            style=TableStyle([
                ("BACKGROUND",   (0, 0), (-1, -1), BRAND_LIGHT),
                ("LEFTPADDING",  (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING",   (0, 0), (0, 0),  10),
                ("BOTTOMPADDING",(0, 1), (-1, -1), 10),
                ("LINEAFTER",    (0, 0), (0, -1),  4, BRAND_ACCENT),
            ])),
        ]

    # ── Style Definitions ──────────────────────────────────────────────────────

    def _build_styles(self) -> dict:
        def S(name, **kwargs):
            return ParagraphStyle(name, **kwargs)

        return {
            "brand":              S("brand",         fontSize=26, textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_LEFT),
            "brand_tag":          S("brand_tag",      fontSize=10, textColor=BRAND_ACCENT, fontName="Helvetica-Bold", alignment=TA_RIGHT, spaceAfter=0),
            "report_type":        S("report_type",    fontSize=14, textColor=BRAND_DARK,   fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4),
            "report_standard":    S("report_std",     fontSize=9,  textColor=LIGHT_GREY,   fontName="Helvetica",      alignment=TA_CENTER, spaceAfter=0),
            "company_name":       S("company_name",   fontSize=22, textColor=BRAND_DARK,   fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4),
            "company_meta":       S("company_meta",   fontSize=10, textColor=LIGHT_GREY,   fontName="Helvetica",      alignment=TA_CENTER, spaceAfter=0),
            "meta_label":         S("meta_label",     fontSize=9,  textColor=LIGHT_GREY,   fontName="Helvetica-Bold"),
            "meta_value":         S("meta_value",     fontSize=9,  textColor=DARK_GREY,    fontName="Helvetica"),
            "score_label":        S("score_label",    fontSize=7,  textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2),
            "score_number":       S("score_number",   fontSize=32, textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=0),
            "score_sub":          S("score_sub",      fontSize=7,  textColor=WHITE,        fontName="Helvetica",      alignment=TA_CENTER),
            "risk_value":         S("risk_value",     fontSize=14, textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER),
            "ce_ready":           S("ce_ready",       fontSize=14, textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER),
            "ce_not_ready":       S("ce_not_ready",   fontSize=12, textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER),
            "confidential":       S("confidential",   fontSize=7,  textColor=LIGHT_GREY,   fontName="Helvetica-Oblique", alignment=TA_CENTER),
            "section_heading":    S("sh",             fontSize=13, textColor=BRAND_DARK,   fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=2),
            "control_heading":    S("ch",             fontSize=10, textColor=WHITE,        fontName="Helvetica-Bold"),
            "control_risk_badge": S("crb",            fontSize=8,  textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER),
            "ctrl_meta":          S("ctrl_meta",      fontSize=8,  textColor=DARK_GREY,    fontName="Helvetica"),
            "gap_priority":       S("gap_priority",   fontSize=8,  textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER),
            "gap_title":          S("gap_title",      fontSize=9,  textColor=DARK_GREY,    fontName="Helvetica-Bold"),
            "gap_body":           S("gap_body",       fontSize=8,  textColor=DARK_GREY,    fontName="Helvetica",      spaceAfter=2, leading=12, leftIndent=4),
            "remediation_header": S("rh",             fontSize=8,  textColor=BRAND_DARK,   fontName="Helvetica-Bold", spaceAfter=1, leftIndent=4),
            "remediation_step":   S("rs",             fontSize=8,  textColor=DARK_GREY,    fontName="Helvetica",      leftIndent=12, spaceAfter=2, leading=11),
            "ncsc_ref":           S("ncsc_ref",       fontSize=7,  textColor=LIGHT_GREY,   fontName="Helvetica-Oblique", leftIndent=4, spaceAfter=4),
            "body":               S("body",           fontSize=9,  textColor=DARK_GREY,    fontName="Helvetica",      spaceAfter=4, leading=14),
            "body_justify":       S("body_j",         fontSize=9,  textColor=DARK_GREY,    fontName="Helvetica",      spaceAfter=4, leading=14, alignment=TA_JUSTIFY),
            "italic":             S("italic",         fontSize=9,  textColor=LIGHT_GREY,   fontName="Helvetica-Oblique", spaceAfter=4),
            "pass_note":          S("pass_note",      fontSize=9,  textColor=GREEN,        fontName="Helvetica-Bold"),
            "priority_num":       S("priority_num",   fontSize=11, textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER),
            "priority_text":      S("priority_text",  fontSize=9,  textColor=DARK_GREY,    fontName="Helvetica",      leading=13),
            "verdict_text":       S("verdict_text",   fontSize=11, textColor=DARK_GREY,    fontName="Helvetica-Bold"),
            "alert_heading":      S("alert_heading",  fontSize=10, textColor=WHITE,        fontName="Helvetica-Bold"),
            "alert_item":         S("alert_item",     fontSize=9,  textColor=RED,          fontName="Helvetica-Bold"),
            "table_header":       S("table_header",   fontSize=8,  textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER),
            "table_cell":         S("table_cell",     fontSize=8,  textColor=DARK_GREY,    fontName="Helvetica"),
            "table_cell_center":  S("table_cell_c",   fontSize=8,  textColor=DARK_GREY,    fontName="Helvetica",      alignment=TA_CENTER),
            "step_item":          S("step_item",      fontSize=9,  textColor=DARK_GREY,    fontName="Helvetica",      leftIndent=8, spaceAfter=5, leading=13),
            "info_heading":       S("info_heading",   fontSize=10, textColor=BRAND_DARK,   fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4),
            "info_body":          S("info_body",      fontSize=8,  textColor=DARK_GREY,    fontName="Helvetica",      leading=13, spaceAfter=8, alignment=TA_JUSTIFY),
            "footer":             S("footer",         fontSize=7,  textColor=LIGHT_GREY,   fontName="Helvetica",      alignment=TA_CENTER),
        }
