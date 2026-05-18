#!/usr/bin/env bash
# bootstrap.sh — einmalig auf einem neuen Mac ausführen
# Installiert Bash 5, setzt es als Default-Shell, verknüpft dotfiles.
#
# Voraussetzung: Homebrew ist bereits installiert, mac-tools ist geklont.
# Aufruf: bash /pfad/zu/mac-tools/shell/bootstrap.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SHELL_DIR="$REPO_DIR/shell"

echo "==> mac-tools bootstrap"
echo "    Repo: $REPO_DIR"

# 1. Homebrew-Bash installieren
echo ""
echo "==> Bash 5 installieren..."
if brew list bash &>/dev/null; then
  echo "    bereits installiert: $(brew list --versions bash)"
else
  brew install bash
fi

BASH5=/opt/homebrew/bin/bash

# 2. In /etc/shells eintragen (braucht sudo)
echo ""
echo "==> $BASH5 in /etc/shells eintragen..."
if grep -qF "$BASH5" /etc/shells; then
  echo "    bereits eingetragen"
else
  echo "$BASH5" | sudo tee -a /etc/shells
  echo "    eingetragen"
fi

# 3. Als Default-Shell setzen (braucht sudo / Passwort)
echo ""
echo "==> Default-Shell auf $BASH5 setzen..."
if [[ "$SHELL" == "$BASH5" ]]; then
  echo "    bereits aktiv"
else
  chsh -s "$BASH5"
  echo "    gesetzt — neues Terminal öffnen damit aktiv"
fi

# 4. dotfiles verknüpfen
echo ""
echo "==> dotfiles symlinken..."

link() {
  local src="$1" dst="$2"
  if [[ -L "$dst" ]]; then
    echo "    $dst → bereits Symlink"
  elif [[ -f "$dst" ]]; then
    echo "    $dst → Backup als ${dst}.before-bootstrap"
    mv "$dst" "${dst}.before-bootstrap"
    ln -s "$src" "$dst"
  else
    ln -s "$src" "$dst"
    echo "    $dst → $src"
  fi
}

link "$SHELL_DIR/bash_profile" "$HOME/.bash_profile"
link "$SHELL_DIR/bashrc"       "$HOME/.bashrc"

# 5. mac-tools-Tools installieren
echo ""
echo "==> mac-tools installieren (make install)..."
make -C "$REPO_DIR" install

echo ""
echo "✓ bootstrap abgeschlossen"
echo "  Neues Terminal öffnen — dann läuft Bash 5."
