#!/usr/bin/env python3
"""
md2pdf – Convert a Markdown file to a formatted A4 PDF.

Usage:
    md2pdf input.md
    md2pdf input.md -o output.pdf
    md2pdf input.md -o /some/dir/report.pdf
"""

import argparse
import re
import sys
from pathlib import Path

# ── Dependencies ───────────────────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle,
    )
except ImportError:
    sys.exit("reportlab not found – run: pip3 install --break-system-packages reportlab")


# ── Colours ────────────────────────────────────────────────────────────────────
COL_BLUE  = colors.HexColor("#1a3a5c")
COL_MID   = colors.HexColor("#2e6da4")
COL_LIGHT = colors.HexColor("#dce8f5")
COL_RULE  = colors.HexColor("#cccccc")
COL_QUOTE = colors.HexColor("#4a7ab5")


# ── Helpers ────────────────────────────────────────────────────────────────────
def escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_inline(text: str) -> str:
    text = escape_xml(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    return text


def parse_table_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


# ── Styles ─────────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("H1", parent=base["Heading1"],
            fontSize=16, leading=20, textColor=COL_BLUE,
            spaceAfter=4, spaceBefore=10),
        "h2": ParagraphStyle("H2", parent=base["Heading2"],
            fontSize=12, leading=16, textColor=COL_MID,
            spaceAfter=2, spaceBefore=8),
        "body": ParagraphStyle("Body", parent=base["Normal"],
            fontSize=10, leading=13, spaceAfter=2),
        "bullet": ParagraphStyle("Bullet", parent=base["Normal"],
            fontSize=10, leading=13, leftIndent=16, bulletIndent=4, spaceAfter=1),
        "ordered": ParagraphStyle("Ordered", parent=base["Normal"],
            fontSize=10, leading=13, leftIndent=20, spaceAfter=1),
        "quote": ParagraphStyle("Quote", parent=base["Normal"],
            fontSize=10, leading=14, textColor=COL_QUOTE,
            leftIndent=12, rightIndent=12, spaceAfter=4, spaceBefore=4,
            fontName="Helvetica-Oblique"),
        "cell": ParagraphStyle("Cell", parent=base["Normal"],
            fontSize=9, leading=12),
        "cell_hdr": ParagraphStyle("CellHdr", parent=base["Normal"],
            fontSize=9, leading=12, fontName="Helvetica-Bold",
            textColor=colors.white),
    }


# ── Table builder ──────────────────────────────────────────────────────────────
def make_table(rows: list[list[str]], styles: dict, page_width: float) -> Table:
    col_count = max(len(r) for r in rows)
    col_w = page_width / col_count

    data = [[Paragraph(parse_inline(c), styles["cell_hdr"]) for c in rows[0]]]
    for row in rows[1:]:
        data.append([Paragraph(parse_inline(c), styles["cell"]) for c in row])

    t = Table(data, colWidths=[col_w] * col_count, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), COL_MID),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, COL_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, COL_RULE),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return t


# ── Parser ─────────────────────────────────────────────────────────────────────
def parse_markdown(lines: list[str], styles: dict, usable_width: float) -> list:
    story = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        if line.startswith("# "):
            story += [Spacer(1, 4),
                      Paragraph(parse_inline(line[2:]), styles["h1"]),
                      HRFlowable(width="100%", thickness=0.8, color=COL_MID, spaceAfter=2)]

        elif line.startswith("## "):
            story += [Spacer(1, 2),
                      Paragraph(parse_inline(line[3:]), styles["h2"])]

        elif line.startswith("> "):
            story.append(Paragraph(parse_inline(line[2:]), styles["quote"]))

        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                raw = lines[i].rstrip("\n")
                if not re.match(r'^\|[\s\-\|]+\|?$', raw):
                    rows.append(parse_table_row(raw))
                i += 1
            if rows:
                story += [make_table(rows, styles, usable_width), Spacer(1, 4)]
            continue

        elif line.startswith(("* ", "- ")):
            story.append(Paragraph(parse_inline(line[2:]), styles["bullet"], bulletText="•"))

        elif re.match(r'^\d+\. ', line):
            m = re.match(r'^(\d+)\. (.+)', line)
            story.append(Paragraph(parse_inline(m.group(2)), styles["ordered"],
                                   bulletText=m.group(1) + "."))

        elif line.strip() == "---":
            story += [Spacer(1, 3),
                      HRFlowable(width="100%", thickness=0.5, color=COL_RULE, spaceAfter=3)]

        elif line.strip():
            story.append(Paragraph(parse_inline(line), styles["body"]))

        else:
            story.append(Spacer(1, 2))

        i += 1
    return story


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Convert Markdown to PDF (A4, formatted).")
    ap.add_argument("input",  help="Input .md file")
    ap.add_argument("-o", "--output", help="Output .pdf file (default: same name as input)")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.exists():
        sys.exit(f"File not found: {src}")

    dst = Path(args.output).resolve() if args.output else src.with_suffix(".pdf")

    MARGIN = 2.0 * cm
    doc = SimpleDocTemplate(str(dst), pagesize=A4,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN)

    styles = build_styles()
    usable_width = A4[0] - 2 * MARGIN

    lines = src.read_text(encoding="utf-8").splitlines(keepends=True)
    story = parse_markdown(lines, styles, usable_width)
    doc.build(story)
    print(f"✓  {dst}")


if __name__ == "__main__":
    main()
