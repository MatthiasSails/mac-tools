# Codex Instructions — mac-tools

Personal CLI tools repo for Matthias's Mac. GitOps-synced via launchd (pulls hourly from GitHub).

Local path: `/Volumes/Rocket_2/DEV/mac-tools/`
GitHub: `https://github.com/MatthiasSails/mac-tools`

---

## Available tools

| Command | What it does |
|---|---|
| `md2pdf input.md` | Markdown → A4 portrait PDF (ReportLab) |
| `halfsheet input.md` | Markdown → A4 landscape half-sheet PDF (cut line, for recipe cards) |

Tools are symlinked into `~/bin/` via `make install`. Add `$HOME/bin` to PATH if not present.

---

## Document processing capabilities (Python, system-wide)

The following libraries are installed system-wide and available to scripts and Claude:

### OCR for scanned PDFs
```bash
# Already installed:
# brew install tesseract tesseract-lang poppler
# pip3 install pytesseract pdf2image --break-system-packages
```
Use when `pdftotext` returns empty output (no text layer). Always pass `lang='deu'` for German documents.

### Apple Numbers files
```bash
# Already installed:
# pip3 install numbers-parser --break-system-packages
```
Reads `.numbers` files directly (cell values + formulas) without an Excel export. See `CLAUDE.md` for full usage examples.

### EML attachments
Standard `import email` — no extra install. Extracts any attachment (PDF, Numbers, etc.) from a `.eml` file saved from Mail.app.

---

## Adding a new tool

1. Create `<name>/` with `<name>.py` and `requirements.txt`
2. Add `bin/<name>` (copy `bin/md2pdf` as template, adjust path)
3. `chmod +x bin/<name> <name>/<name>.py`
4. Commit + push → launchd installs within the hour, or run `make install` immediately

---

## Standing rules

- Never commit without Matthias's explicit approval
- This is a public repo — no secrets, no personal data in committed files
- Working language: English in all file content and commits
