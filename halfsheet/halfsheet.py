#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
halfsheet – Convert a Markdown file to an A4-landscape half-sheet PDF.

The content fills the LEFT half of the page.  A dashed line marks the
centre so the sheet can be cut or folded — ideal for reference cards
placed next to a machine, on a desk, etc.

Usage:
    halfsheet recipe.md
    halfsheet recipe.md -o output.pdf
    halfsheet recipe.md --title "My Title"
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.platypus import Table, TableStyle, Paragraph, KeepTogether
except ImportError:
    sys.exit("reportlab not found – run: pip3 install --break-system-packages reportlab")


# ── Page geometry ─────────────────────────────────────────────────────────────

PAGE_W, PAGE_H = A4[1], A4[0]   # A4 landscape: 841.9 × 595.3 pt
HALF_W  = PAGE_W / 2
MARGIN_L = 14 * mm
MARGIN_R = 10 * mm
MARGIN_T = 14 * mm
MARGIN_B = 12 * mm
CONTENT_W = HALF_W - MARGIN_L - MARGIN_R


# ── Colours ───────────────────────────────────────────────────────────────────

C_HEADING  = colors.HexColor("#1a1a1a")
C_SECTION  = colors.HexColor("#555555")
C_RULE     = colors.HexColor("#cccccc")
C_TH_BG    = colors.HexColor("#333333")
C_ROW_ALT  = colors.HexColor("#f7f7f7")
C_DASH     = colors.HexColor("#aaaaaa")
C_WORKFLOW = colors.HexColor("#f0f0f0")


# ── Styles ────────────────────────────────────────────────────────────────────

SCALE = 1.0  # set from --scale CLI arg; 1.0 = unchanged default sizing

def build_styles():
    base = getSampleStyleSheet()
    def s(name, font="Helvetica", size=9, leading=None, color=colors.black, **kw):
        size = size * SCALE
        return ParagraphStyle(name, fontName=font, fontSize=size,
                              leading=(leading * SCALE) if leading else size * 1.3,
                              textColor=color, **kw)
    return {
        "h1":     s("h1",  "Helvetica-Bold", 11, leading=13, color=C_HEADING),
        "h2":     s("h2",  "Helvetica-Bold",  9, color=C_HEADING, spaceBefore=4),
        "sub":    s("sub", "Helvetica",        8, color=colors.HexColor("#444444")),
        "body":   s("body","Helvetica",       8.5, leading=11),
        "bullet": s("bul", "Helvetica",       8.5, leading=11, leftIndent=10),
        "strong": s("str", "Helvetica-Bold",  8.5, leading=11),
        "th":     s("th",  "Helvetica-Bold",  8.5, leading=11, color=colors.white),
        "tc":     s("tc",  "Helvetica",       8.5, leading=11),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def escape_xml(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline(t):
    t = escape_xml(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', t)
    return t

def hline(c, y):
    c.setLineWidth(0.4)
    c.setStrokeColor(C_RULE)
    c.line(MARGIN_L, y, HALF_W - MARGIN_R, y)

def section_head(c, text, y):
    c.setFont("Helvetica-Bold", 7.5 * SCALE)
    c.setFillColor(C_SECTION)
    c.drawString(MARGIN_L, y, text.upper())
    c.setFillColor(colors.black)
    return 9 * SCALE

def draw_para(c, text, style, x, y):
    p = Paragraph(text, style)
    w, h = p.wrap(CONTENT_W, 9999)
    p.drawOn(c, x, y - h)
    return h

def draw_table(c, table, x, y):
    w, h = table.wrap(CONTENT_W, 9999)
    table.drawOn(c, x, y - h)
    return h

def parse_table_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

def is_separator_row(line):
    return bool(re.match(r'^\|[\s\-:\|]+\|?$', line.strip()))

def make_table(rows, styles):
    col_count = max(len(r) for r in rows)
    col_w = CONTENT_W / col_count

    data = [[Paragraph(inline(c), styles["th"]) for c in rows[0]]]
    for row in rows[1:]:
        # pad short rows
        padded = row + [""] * (col_count - len(row))
        data.append([Paragraph(inline(c), styles["tc"]) for c in padded])

    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), C_TH_BG),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_ROW_ALT, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_RULE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
    ])
    t = Table(data, colWidths=[col_w] * col_count)
    t.setStyle(ts)
    return t


# ── Markdown parser / renderer ────────────────────────────────────────────────

def render(c, lines, styles):
    y = PAGE_H - MARGIN_T
    i = 0

    def gap(pt):
        nonlocal y
        y -= pt

    while i < len(lines):
        line = lines[i].rstrip("\n")

        # H1
        if line.startswith("# "):
            h = draw_para(c, inline(line[2:]), styles["h1"], MARGIN_L, y)
            y -= h + 1 * SCALE

        # H2 → rendered as uppercase section label
        elif line.startswith("## "):
            gap(6 * SCALE)          # separation from the block above
            hline(c, y)
            gap(8 * SCALE)          # drop clear of the cap height before the label
            y -= section_head(c, line[3:], y) + 2 * SCALE

        # H3 → bold body
        elif line.startswith("### "):
            h = draw_para(c, f"<b>{inline(line[4:])}</b>", styles["body"], MARGIN_L, y)
            y -= h + 2 * SCALE

        # HR
        elif line.strip() == "---":
            gap(2 * SCALE)
            hline(c, y)
            gap(3 * SCALE)

        # Table
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                raw = lines[i].rstrip("\n")
                if not is_separator_row(raw):
                    rows.append(parse_table_row(raw))
                i += 1
            if rows:
                h = draw_table(c, make_table(rows, styles), MARGIN_L, y)
                y -= h + 4 * SCALE
            continue

        # Bullet list — collect run and render as workflow boxes if consecutive
        elif line.startswith(("* ", "- ")):
            bullets = []
            while i < len(lines) and lines[i].startswith(("* ", "- ")):
                bullets.append(lines[i].rstrip("\n")[2:])
                i += 1
            bullet_h = _render_bullets(c, bullets, styles, y)
            y -= bullet_h + 4 * SCALE
            continue

        # Ordered list
        elif re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                m = re.match(r'^\d+\. (.+)', lines[i].rstrip("\n"))
                items.append(m.group(1))
                i += 1
            _render_steps(c, items, y)
            y -= _steps_height() + 4 * SCALE
            continue

        # Blank line
        elif not line.strip():
            gap(3 * SCALE)

        # Regular paragraph
        else:
            h = draw_para(c, inline(line), styles["body"], MARGIN_L, y)
            y -= h + 2 * SCALE

        i += 1


def _render_bullets(c, items, styles, top_y):
    y = top_y
    for item in items:
        h = draw_para(c, "• " + inline(item), styles["bullet"], MARGIN_L, y)
        y -= h + 1 * SCALE
    return top_y - y

def _steps_height():
    return 16 * SCALE

def _render_steps(c, steps, y):
    box_w = CONTENT_W / len(steps)
    box_h = 15 * SCALE
    by = y - box_h
    for i, step in enumerate(steps):
        bx = MARGIN_L + i * box_w
        c.setFillColor(C_WORKFLOW)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.4)
        c.rect(bx, by, box_w - 1, box_h, fill=1, stroke=1)
        c.setFillColor(colors.black)
        label = f"{i+1}  {step}"
        font_size = 7.2 * SCALE
        c.setFont("Helvetica", font_size)
        tw = c.stringWidth(label, "Helvetica", font_size)
        c.drawString(bx + (box_w - 1 - tw) / 2, by + (box_h - font_size) / 2 + 1, label)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Markdown → A4-landscape half-sheet PDF")
    ap.add_argument("input",  help="Input .md file")
    ap.add_argument("-o", "--output", help="Output .pdf (default: same name as input)")
    ap.add_argument("--title", help="PDF metadata title (default: derived from filename)")
    ap.add_argument("--scale", type=float, default=1.0,
                     help="Font/spacing scale factor, e.g. 1.4 for larger text (default: 1.0)")
    args = ap.parse_args()

    global SCALE
    SCALE = args.scale

    src = Path(args.input).resolve()
    if not src.exists():
        sys.exit(f"File not found: {src}")

    dst = Path(args.output).resolve() if args.output else src.with_suffix(".pdf")
    title = args.title or src.stem.replace("-", " ").replace("_", " ").title()

    c = rl_canvas.Canvas(str(dst), pagesize=(PAGE_W, PAGE_H))
    c.setTitle(title)

    styles = build_styles()
    lines = src.read_text(encoding="utf-8").splitlines(keepends=True)
    render(c, lines, styles)

    # dashed centre fold/cut line
    c.setLineWidth(0.6)
    c.setStrokeColor(C_DASH)
    c.setDash(4, 3)
    c.line(HALF_W, MARGIN_B, HALF_W, PAGE_H - MARGIN_B)
    c.setDash()

    c.save()
    print(f"  {dst}")


if __name__ == "__main__":
    main()
