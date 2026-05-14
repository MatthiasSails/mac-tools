# mac-tools

Personal CLI tools, GitOps-synced to this Mac via launchd.

## Setup (once)

```bash
cd /Volumes/Rocket_2/DEV/mac-tools
make install                           # installs deps + symlinks ~/bin/*

# Add ~/bin to PATH if not already there (in ~/.zprofile):
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile

# Load the launchd sync agent:
cp launchd/com.matthias.mac-tools-sync.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.matthias.mac-tools-sync.plist
```

After that, every push to `main` lands on the Mac within ~1 hour automatically.

## Tools

| Command | Description |
|---|---|
| `md2pdf input.md` | Convert Markdown to a formatted A4 PDF |
| `md2pdf input.md -o report.pdf` | Explicit output path |
| `halfsheet input.md` | Markdown → A4-landscape half-sheet PDF (left half, dashed cut line) |
| `halfsheet input.md -o card.pdf` | Explicit output path |

### halfsheet

Converts any Markdown file to a reference card: content fills the **left half** of an A4 landscape page, right half stays blank, dashed line marks the fold/cut. Ideal for recipe cards, cheat sheets, or machine-side reference cards.

Supports: headings (`#`, `##`), paragraphs, tables, bullet lists, ordered lists (rendered as step boxes), horizontal rules (`---`).

Example:
```bash
halfsheet halfsheet/examples/espresso-brasilien.md
```

## Manual update

```bash
cd /Volumes/Rocket_2/DEV/mac-tools && make update
```

## Adding a new tool

1. Create `<toolname>/` directory with the script and a `requirements.txt`
2. Add a wrapper to `bin/<toolname>` (see `bin/md2pdf` as template)
3. `make install` – done
