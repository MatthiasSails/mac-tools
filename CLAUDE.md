# mac-tools — Claude context

Personal CLI tools at `/Volumes/Rocket_2/DEV/mac-tools/`.
Each tool lives in its own subdirectory; `bin/` holds thin shell wrappers.
`make install` installs deps and symlinks `bin/*` into `~/bin/`.

## Available tools

### md2pdf
`mac-tools/md2pdf/md2pdf.py` — Markdown → formatted A4 portrait PDF.
Uses ReportLab `SimpleDocTemplate` + Platypus flowables.

**Known limitations (relevant when targeting one-page cheat sheets):**
- **No fenced code-block handling.** Lines starting with ``` are rendered as visible body text (the literal backticks appear in the PDF) and the lines inside the fence are each parsed individually as body paragraphs with `spaceAfter=2`. To save space, use inline backticks (`` `code` ``) or bullet lists instead of fences.
- **Blank lines render as `Spacer(1, 2)`.** Each empty line in the MD adds vertical air. For dense layouts, strip blank lines aggressively — the parser does not require them between sections.
- **Margins fixed at 2 cm** and styles `spaceBefore`/`leading` are hard-coded in `build_styles()`. If a cheat sheet is one line over, edit those constants rather than torturing the MD.

### halfsheet
`mac-tools/halfsheet/halfsheet.py` — Markdown → A4 landscape **half-sheet** PDF.

Layout: content on **left half** (148 mm wide), right half blank, dashed centre line for cutting/folding.
Use for: recipe cards, cheat sheets, reference cards placed next to a machine.

**To generate a PDF:**
```bash
python3 /Volumes/Rocket_2/DEV/mac-tools/halfsheet/halfsheet.py input.md
python3 /Volumes/Rocket_2/DEV/mac-tools/halfsheet/halfsheet.py input.md -o output.pdf
```
Or via the installed wrapper: `halfsheet input.md`

**Markdown features supported:**
- `# Title` — large heading
- `## Section` — rendered as uppercase section label with rule above
- `### Sub` — bold body text
- `| table |` — formatted table with dark header row
- `1. Step` — rendered as a row of numbered step boxes (workflow strip)
- `* item` / `- item` — bullet list
- `---` — horizontal rule
- `**bold**`, `*italic*` — inline formatting
- Regular paragraphs

**Critical implementation detail — table cells must use Paragraph objects:**
Plain strings in ReportLab Table cells are rendered via `drawString` without
encoding processing. Spaces and non-ASCII chars (°, ü, ö, ä, ·, –) render as
black boxes. Always wrap every cell value in a `Paragraph(str(cell), style)`.
This is already done in `halfsheet.py` — never revert to raw strings.

**Espresso recipe examples:**
- `mac-tools/halfsheet/examples/espresso-brasilien.md` — Brasilien COOPFAM Natural

Update the relevant `.md` file when the recipe changes, then re-run halfsheet.

**If content overflows the page** (bottom sections cut off): reduce spacing constants in `halfsheet.py`:
- `TOPPADDING` / `BOTTOMPADDING` in `make_table()` (default 2 — go lower if needed)
- HR gaps: `gap(2)` / `gap(3)` in the `---` block of `render()`
- H1 font size: `build_styles()` → `"h1"` entry (currently 11pt)

## System dependencies

### poppler (pdftotext, pdfinfo)
Required for PDF text extraction and metadata reading. Not installed by default on macOS.

```bash
brew install poppler
```

Provides: `pdftotext`, `pdfinfo`, `pdfimages`. Without it, any attempt to extract text from PDFs fails silently or with "command not found".

---

## Adding a new tool

1. Create `<name>/` with `<name>.py` and `requirements.txt`
2. Add `bin/<name>` (copy `bin/md2pdf` as template, adjust path)
3. `chmod +x bin/<name> <name>/<name>.py`
4. `make install`
