# -*- coding: utf-8 -*-
"""Generate PDF from phreshphish_final_report.md for course submission."""
from __future__ import annotations

import re
from pathlib import Path

from fpdf import FPDF
from fpdf.fonts import FontFace

REPORT_DIR = Path(__file__).resolve().parent
MD_PATH = REPORT_DIR / "phreshphish_final_report.md"
PDF_PATH = REPORT_DIR / "phreshphish_final_report.pdf"

META_LINE = re.compile(r"^\*\*[^*]+\*\*:")
ORDERED_LIST = re.compile(r"^\d+\.\s+")


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
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    for ch, repl in (("\u2192", "->"), ("\u2014", "-"), ("\u00b1", "+/-")):
        text = text.replace(ch, repl)
    return text.strip()


def parse_markdown(path: Path) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if not stripped:
            i += 1
            continue
        if stripped == "---":
            blocks.append(("hr", ""))
            i += 1
            continue
        if raw.startswith("# "):
            blocks.append(("h1", strip_md_inline(raw[2:])))
            i += 1
            continue
        if raw.startswith("## "):
            blocks.append(("h2", strip_md_inline(raw[3:])))
            i += 1
            continue
        if raw.startswith("### "):
            blocks.append(("h3", strip_md_inline(raw[4:])))
            i += 1
            continue
        if raw.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            table_lines = [raw]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            blocks.append(("table", "\n".join(table_lines)))
            continue
        if META_LINE.match(stripped):
            blocks.append(("meta", strip_md_inline(stripped)))
            i += 1
            continue
        if stripped.startswith("- "):
            blocks.append(("li", strip_md_inline(stripped[2:])))
            i += 1
            continue
        if ORDERED_LIST.match(stripped):
            blocks.append(("oli", strip_md_inline(ORDERED_LIST.sub("", stripped))))
            i += 1
            continue

        # Paragraph block: lines until blank line; hard breaks when line ends with two spaces
        parts: list[str] = []
        while i < len(lines):
            line = lines[i]
            s = line.strip()
            if not s or s == "---":
                break
            if line.startswith("#") or s.startswith("|") or META_LINE.match(s):
                break
            if s.startswith("- ") or ORDERED_LIST.match(s):
                break
            hard_break = line.endswith("  ")
            parts.append(strip_md_inline(s))
            i += 1
            if hard_break:
                blocks.append(("body", " ".join(parts)))
                parts = []
        if parts:
            blocks.append(("body", " ".join(parts)))
        if i < len(lines) and not lines[i].strip():
            i += 1
    return blocks


class ReportPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Report", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def write_block(pdf: ReportPDF, text: str, size: int, style: str = "", lh: float = 6.0, after: float = 2.0) -> None:
    pdf.set_font("Report", style, size)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pdf.epw, lh, text)
    pdf.ln(after)


def split_md_table_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    cells: list[str] = []
    buf: list[str] = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def parse_table_rows(raw: str) -> list[list[str]]:
    rows = [r for r in raw.splitlines() if r.strip()]
    if len(rows) < 2:
        return []
    data_rows = [rows[0]] + [r for r in rows[2:] if not re.match(r"^\|[-:\s|]+\|$", r)]
    return [[strip_md_inline(c) for c in split_md_table_row(row)] for row in data_rows]


def column_widths(pdf: ReportPDF, n_cols: int) -> tuple[float, ...] | None:
    total_w = pdf.epw
    if n_cols >= 6:
        weights = [2.2] + [1.0] * (n_cols - 1)
    elif n_cols == 4:
        weights = [1.2, 1.4, 1.6, 1.6]
    elif n_cols == 5:
        weights = [1.0, 0.7, 1.2, 1.2, 1.2]
    elif n_cols == 2:
        weights = [1.0, 2.8]
    elif n_cols == 3:
        weights = [1.0, 1.2, 1.2]
    else:
        return None
    s = sum(weights)
    return tuple(total_w * w / s for w in weights)


def render_table(pdf: ReportPDF, raw: str) -> None:
    data = parse_table_rows(raw)
    if not data:
        return

    n_cols = len(data[0])
    font_size = 7 if n_cols >= 6 else 8
    line_h = 5 if n_cols >= 6 else 6
    widths = column_widths(pdf, n_cols)

    pdf.ln(2)
    headings = FontFace(family="Report", emphasis="BOLD", size_pt=font_size)
    table_kwargs = dict(
        width=pdf.epw,
        line_height=line_h,
        text_align="LEFT",
        first_row_as_headings=True,
        headings_style=headings,
        wrapmode="WORD",
    )
    if widths:
        table_kwargs["col_widths"] = widths

    with pdf.table(**table_kwargs) as table:
        pdf.set_font("Report", "", font_size)
        for row in data:
            tr = table.row()
            for cell in row:
                tr.cell(cell)
    pdf.ln(4)


def build_pdf() -> None:
    font_path, bold_path = find_fonts()
    blocks = parse_markdown(MD_PATH)

    pdf = ReportPDF()
    pdf.set_margins(25, 20, 25)
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.add_font("Report", "", font_path)
    pdf.add_font("Report", "B", bold_path)
    pdf.add_page()

    for kind, content in blocks:
        if kind == "h1":
            pdf.ln(2)
            write_block(pdf, content, 16, "B", lh=8, after=4)
        elif kind == "meta":
            write_block(pdf, content, 10, "", lh=5.5, after=1.5)
        elif kind == "h2":
            pdf.ln(5)
            write_block(pdf, content, 13, "B", lh=7, after=3)
        elif kind == "h3":
            pdf.ln(3)
            write_block(pdf, content, 11, "B", lh=6.5, after=2)
        elif kind == "body":
            write_block(pdf, content, 10, "", lh=6, after=4)
        elif kind == "li":
            pdf.set_font("Report", "", 10)
            pdf.set_x(pdf.l_margin + 5)
            pdf.multi_cell(pdf.epw - 5, 6, f"- {content}")
            pdf.ln(1.5)
        elif kind == "oli":
            pdf.set_font("Report", "", 10)
            pdf.set_x(pdf.l_margin + 5)
            pdf.multi_cell(pdf.epw - 5, 6, content)
            pdf.ln(1.5)
        elif kind == "table":
            render_table(pdf, content)
        elif kind == "hr":
            pdf.ln(6)

    pdf.output(str(PDF_PATH))
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
