# mac-tools — Claude context

Personal CLI tools at `/Volumes/Rocket_2/DEV/mac-tools/`.
Each tool lives in its own subdirectory; `bin/` holds thin shell wrappers.
`make install` installs deps and symlinks `bin/*` into `~/bin/`.

## Available tools

### md2pdf
`mac-tools/md2pdf/md2pdf.py` — Markdown → formatted A4 portrait PDF.
Uses ReportLab `SimpleDocTemplate` + Platypus flowables.

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

**Espresso recipe example:**
`mac-tools/halfsheet/examples/espresso-brasilien.md`
Generates the recipe card for the Brasilien COOPFAM Arabica Natural.
Update this file when the recipe changes, then re-run halfsheet.

## Adding a new tool

1. Create `<name>/` with `<name>.py` and `requirements.txt`
2. Add `bin/<name>` (copy `bin/md2pdf` as template, adjust path)
3. `chmod +x bin/<name> <name>/<name>.py`
4. `make install`
