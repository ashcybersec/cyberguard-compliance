import os
import uuid
import zipfile
from datetime import date
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ── Brand colours ──────────────────────────────────────────────────────────────
NAVY  = RGBColor(0x0D, 0x1B, 0x2A)
CYAN  = RGBColor(0x00, 0xC2, 0xCB)
GREY  = RGBColor(0x44, 0x55, 0x66)
BLACK = RGBColor(0x11, 0x11, 0x11)

DOCUMENT_TITLES = {
    "scope_statement":            "Cyber Essentials — Scope Statement",
    "information_security_policy":"Information Security Policy",
    "access_control_policy":      "Access Control Policy",
    "patch_management_policy":    "Patch Management Policy",
    "firewall_network_policy":    "Firewall & Network Security Policy",
    "malware_protection_policy":  "Malware Protection Policy",
    "asset_register_guidance":    "Asset Register — Guidance & Template",
}

DOCUMENT_REFS = {
    "scope_statement":            "CG-SCOPE-001",
    "information_security_policy":"CG-POL-001",
    "access_control_policy":      "CG-POL-002",
    "patch_management_policy":    "CG-POL-003",
    "firewall_network_policy":    "CG-POL-004",
    "malware_protection_policy":  "CG-POL-005",
    "asset_register_guidance":    "CG-REG-001",
}


class EvidencePackBuilder:
    """Converts AI-generated document text into branded Word (.docx) files and zips them."""

    OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "reports")

    def __init__(self):
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def build_zip(self, company_name: str, documents: dict) -> str:
        """
        Build all 7 Word documents and return path to ZIP archive.
        """
        session_id = uuid.uuid4().hex[:8]
        safe_name  = company_name.replace(" ", "_").replace("/", "-")
        zip_path   = f"{self.OUTPUT_DIR}/CyberGuard_EvidencePack_{safe_name}_{session_id}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, (doc_key, content) in enumerate(documents.items(), 1):
                title    = DOCUMENT_TITLES.get(doc_key, doc_key.replace("_", " ").title())
                ref      = DOCUMENT_REFS.get(doc_key, f"CG-DOC-{i:03d}")
                filename = f"{i:02d}_{doc_key}.docx"
                docx_bytes = self._build_docx(company_name, title, ref, content)
                zf.writestr(filename, docx_bytes)

        return zip_path

    def _build_docx(self, company: str, title: str, ref: str, content: str) -> bytes:
        """Build a single branded Word document and return bytes."""
        doc = Document()

        # ── Page margins ──────────────────────────────────────────────────────
        for section in doc.sections:
            section.top_margin    = Cm(2.0)
            section.bottom_margin = Cm(2.0)
            section.left_margin   = Cm(2.5)
            section.right_margin  = Cm(2.5)

        # ── Header ────────────────────────────────────────────────────────────
        header = doc.sections[0].header
        htbl   = header.add_table(1, 2, width=Inches(6))
        htbl.style = "Table Grid"
        self._remove_table_borders(htbl)

        left  = htbl.cell(0, 0).paragraphs[0]
        right = htbl.cell(0, 1).paragraphs[0]

        run_l = left.add_run("CyberGuard")
        run_l.bold      = True
        run_l.font.size = Pt(11)
        run_l.font.color.rgb = CYAN
        left.alignment  = WD_ALIGN_PARAGRAPH.LEFT

        run_r = right.add_run(f"{ref}  |  {company}")
        run_r.font.size      = Pt(8)
        run_r.font.color.rgb = GREY
        right.alignment      = WD_ALIGN_PARAGRAPH.RIGHT

        self._add_hline(header)

        # ── Cover block ───────────────────────────────────────────────────────
        doc.add_paragraph()

        p_company = doc.add_paragraph()
        r = p_company.add_run(company.upper())
        r.bold = True
        r.font.size      = Pt(9)
        r.font.color.rgb = GREY
        r.font.name      = "Calibri"
        p_company.alignment = WD_ALIGN_PARAGRAPH.LEFT

        p_title = doc.add_paragraph()
        r2 = p_title.add_run(title)
        r2.bold          = True
        r2.font.size     = Pt(20)
        r2.font.color.rgb = NAVY
        r2.font.name     = "Calibri"
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Cyan underline bar
        self._add_colour_bar(doc, CYAN)

        meta = doc.add_paragraph()
        meta.add_run(
            f"Version 1.0  ·  {date.today().strftime('%d %B %Y')}  ·  "
            f"NCSC Cyber Essentials v3.3 Aligned"
        ).font.size = Pt(9)
        meta.runs[0].font.color.rgb = GREY
        meta.alignment = WD_ALIGN_PARAGRAPH.LEFT

        doc.add_paragraph()

        # ── Body content ──────────────────────────────────────────────────────
        self._render_content(doc, content)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = doc.sections[0].footer
        self._add_hline(footer)
        fp = footer.add_paragraph()
        fp.add_run(
            f"© {date.today().year} CyberGuard — ashcybersec.co.uk  ·  "
            f"Aligned to NCSC Cyber Essentials v3.3  ·  {ref}"
        ).font.size = Pt(8)
        fp.runs[0].font.color.rgb = GREY
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # ── Return bytes ──────────────────────────────────────────────────────
        import io
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def _render_content(self, doc: Document, content: str):
        """
        Parse the AI-generated content and render it into the Word document.
        Handles headings (lines starting with ##), tables (| delimited),
        bullet lists (- prefix), and regular paragraphs.
        """
        # Unescape literal \n sequences from JSON string content
        content = content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
        # Strip any JSON wrapper if present
        if content.strip().startswith('{'):
            try:
                import json
                parsed = json.loads(content)
                content = list(parsed.values())[0] if parsed else content
            except Exception:
                pass
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines — add spacing
            if not line:
                i += 1
                continue

            # Heading level 1
            if line.startswith("# ") and not line.startswith("##"):
                p = doc.add_heading(line[2:].strip(), level=1)
                self._style_heading(p, 1)
                i += 1
                continue

            # Heading level 2
            if line.startswith("## "):
                p = doc.add_heading(line[3:].strip(), level=2)
                self._style_heading(p, 2)
                i += 1
                continue

            # Heading level 3
            if line.startswith("### "):
                p = doc.add_heading(line[4:].strip(), level=3)
                self._style_heading(p, 3)
                i += 1
                continue

            # Table (collect all consecutive | lines)
            if line.startswith("|"):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1
                self._render_table(doc, table_lines)
                continue

            # Bullet list item
            if line.startswith("- ") or line.startswith("* "):
                p = doc.add_paragraph(line[2:].strip(), style="List Bullet")
                p.runs[0].font.size = Pt(10)
                i += 1
                continue

            # Numbered list item
            if len(line) > 2 and line[0].isdigit() and line[1] in ".)" :
                text = line[2:].strip()
                p = doc.add_paragraph(text, style="List Number")
                p.runs[0].font.size = Pt(10)
                i += 1
                continue

            # Bold line (standalone ** ** line = informal heading)
            if line.startswith("**") and line.endswith("**") and len(line) > 4:
                p = doc.add_paragraph()
                r = p.add_run(line.strip("*").strip())
                r.bold           = True
                r.font.size      = Pt(10.5)
                r.font.color.rgb = NAVY
                i += 1
                continue

            # Regular paragraph
            p = doc.add_paragraph(line)
            p.runs[0].font.size = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            i += 1

    def _render_table(self, doc: Document, table_lines: list):
        """Render a markdown-style pipe table into a Word table."""
        rows = []
        for line in table_lines:
            # Skip separator rows (---|---| etc)
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            rows.append(cells)

        if not rows:
            return

        ncols = max(len(r) for r in rows)
        tbl   = doc.add_table(rows=len(rows), cols=ncols)
        tbl.style = "Table Grid"

        for ri, row_data in enumerate(rows):
            for ci, cell_text in enumerate(row_data):
                if ci >= ncols:
                    break
                cell = tbl.cell(ri, ci)
                cell.text = cell_text
                run = cell.paragraphs[0].runs
                if run:
                    run[0].font.size = Pt(9)
                    if ri == 0:
                        run[0].bold = True
                        run[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                        self._set_cell_bg(cell, "0D1B2A")

        doc.add_paragraph()

    def _style_heading(self, p, level: int):
        for run in p.runs:
            run.font.name = "Calibri"
            if level == 1:
                run.font.size      = Pt(15)
                run.font.color.rgb = NAVY
                run.bold           = True
            elif level == 2:
                run.font.size      = Pt(12)
                run.font.color.rgb = NAVY
                run.bold           = True
            else:
                run.font.size      = Pt(10.5)
                run.font.color.rgb = GREY
                run.bold           = True

    def _add_hline(self, parent):
        """Add a thin horizontal line paragraph."""
        p = parent.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "4")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), "00C2CB")
        pBdr.append(bottom)
        pPr.append(pBdr)

    def _add_colour_bar(self, doc: Document, colour: RGBColor):
        """Add a thin coloured paragraph border as a visual divider."""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after  = Pt(6)
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "12")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), f"{colour[0]:02X}{colour[1]:02X}{colour[2]:02X}")
        pBdr.append(bottom)
        pPr.append(pBdr)

    def _set_cell_bg(self, cell, hex_color: str):
        """Set table cell background colour."""
        tc   = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd  = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), hex_color)
        tcPr.append(shd)

    def _remove_table_borders(self, table):
        """Remove all borders from a table (used for header layout table)."""
        tbl  = table._tbl
        tblPr = tbl.tblPr
        if tblPr is None:
            tblPr = OxmlElement("w:tblPr")
            tbl.insert(0, tblPr)
        tblBorders = OxmlElement("w:tblBorders")
        for border_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            border = OxmlElement(f"w:{border_name}")
            border.set(qn("w:val"), "none")
            tblBorders.append(border)
        tblPr.append(tblBorders)
