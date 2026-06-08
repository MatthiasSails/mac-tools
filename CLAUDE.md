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

### tesseract + pytesseract + pdf2image (OCR for scanned PDFs)
Required when a PDF contains no text layer (e.g. scanned documents from a RICOH or similar office copier). `pdftotext` returns empty output in this case.

```bash
brew install tesseract tesseract-lang poppler
pip3 install pytesseract pdf2image --break-system-packages
```

Usage:
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scan.pdf', dpi=300)
for img in images:
    text = pytesseract.image_to_string(img, lang='deu')
    print(text)
```

Use `lang='deu'` for German documents, `lang='eng'` for English. `tesseract-lang` installs all language packs.

### numbers-parser (Apple Numbers files)
Reads `.numbers` files directly — cell values, formulas, sheet and table names — without requiring an Excel export.

```bash
pip3 install numbers-parser --break-system-packages
```

Usage:
```python
from numbers_parser import Document

doc = Document('file.numbers')
for sheet in doc.sheets:
    for table in sheet.tables:
        for i, row in enumerate(table.iter_rows()):
            for j, cell in enumerate(row):
                print(cell.value, cell.formula)  # formula is None if cell has no formula
```

`.numbers` files are ZIP archives containing Apple Protobuf (`.iwa`) files. `numbers-parser` reverse-engineered the schema. For a quick visual overview without full parsing, extract `preview.jpg` from the ZIP.

### EML file processing (email attachments)
`.eml` files (dragged from Mail.app) can be parsed with Python's standard `email` library to extract attachments.

```python
import email

with open('message.eml', 'rb') as f:
    msg = email.message_from_binary_file(f)

for part in msg.walk():
    filename = part.get_filename()
    if filename:
        payload = part.get_payload(decode=True)
        with open(filename, 'wb') as out:
            out.write(payload)
```

Combine with the PDF OCR or numbers-parser pipelines above to process scanned invoices or spreadsheets received by email.

---

## Adding a new tool

1. Create `<name>/` with `<name>.py` and `requirements.txt`
2. Add `bin/<name>` (copy `bin/md2pdf` as template, adjust path)
3. `chmod +x bin/<name> <name>/<name>.py`
4. `make install`
