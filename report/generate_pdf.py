# -*- coding: utf-8 -*-
"""Generate PDF from phreshphish_final_report.md for course submission."""
from __future__ import annotations

import re
from pathlib import Path

from fpdf import FPDF

REPORT_DIR = Path(__file__).resolve().parent
MD_PATH = REPORT_DIR / "phreshphish_final_report.md"
PDF_PATH = REPORT_DIR / "phreshphish_final_report.pdf"


def find_fonts() -> tuple[str, str]:
    candidates = [
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
        (Path("C:/Windows/Fonts/Arial.ttf"), Path("C:/Windows/Fonts/Arialbd.ttf")),
    ]
    for regular, bold in candidates:
        if regular.exists():
            bold_path = str(bold) if bold.exists() else str(regular)
            return str(regular), bold_path
    raise FileNotFoundError("Arial font not found under C:/Windows/Fonts")


def strip_md_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    for ch, repl in (("\u2192", "->"), ("\u2014", "-"), ("\u00b1", "+/-")):
        text = text.replace(ch, repl)
    return text.strip()


def parse_markdown(path: Path) -> list[tuple[str, str]]:
    """Return list of (level, content) where level is title/body/table."""
    blocks: list[tuple[str, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            blocks.append(("h1", strip_md_inline(line[2:])))
        elif line.startswith("## "):
            blocks.append(("h2", strip_md_inline(line[3:])))
        elif line.startswith("### "):
            blocks.append(("h3", strip_md_inline(line[4:])))
        elif line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            blocks.append(("table", "\n".join(table_lines)))
            continue
        elif line.strip() == "---":
            blocks.append(("hr", ""))
        elif line.strip():
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
                if lines[i].startswith("|"):
                    break
                if lines[i].strip() == "---":
                    break
                para.append(lines[i])
                i += 1
            blocks.append(("body", strip_md_inline(" ".join(para))))
            continue
        i += 1
    return blocks


class ReportPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Report", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def render_table(pdf: ReportPDF, raw: str) -> None:
    rows = [r for r in raw.splitlines() if r.strip()]
    if len(rows) < 2:
        return
    data_rows = [rows[0]] + [r for r in rows[2:] if not re.match(r"^\|[-:\s|]+\|$", r)]
    for idx, row in enumerate(data_rows):
        cells = [c.strip() for c in row.strip("|").split("|")]
        line = " | ".join(strip_md_inline(c) for c in cells)
        pdf.set_font("Report", "B" if idx == 0 else "", 7)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 4.5, line)
    pdf.ln(2)


def build_pdf() -> None:
    font_path, bold_path = find_fonts()
    blocks = parse_markdown(MD_PATH)

    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_font("Report", "", font_path)
    pdf.add_font("Report", "B", bold_path)
    pdf.add_page()

    for kind, content in blocks:
        if kind == "h1":
            pdf.ln(4)
            pdf.set_font("Report", "B", 16)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 9, content)
            pdf.ln(3)
        elif kind == "h2":
            pdf.ln(6)
            pdf.set_font("Report", "B", 13)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 8, content)
            pdf.ln(2)
        elif kind == "h3":
            pdf.ln(3)
            pdf.set_font("Report", "B", 11)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 7, content)
            pdf.ln(1)
        elif kind == "table":
            render_table(pdf, content)
        elif kind == "hr":
            pdf.ln(4)
        elif kind == "body":
            pdf.set_font("Report", "", 10)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 5.5, content)
            pdf.ln(1)

    pdf.output(str(PDF_PATH))
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
