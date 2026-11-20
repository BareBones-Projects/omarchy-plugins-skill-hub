#!/usr/bin/env bash
# BareBones Projects, Designed by: Justin Levesque-Welsch
# Installs the backend without touching the Omarchy shell or bar configuration.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
HOME_DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
DEST="$HOME_DATA/omarchy-skill-hub/runtime"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$DEST" "$HOME_DATA/applications" "$BIN_DIR" "$HOME_CONFIG/omarchy-skill-hub"
# Copy only our runtime assets; preserve the existing DB and config.
cp -R "$SRC/app" "$DEST/"
install -m755 "$SRC/bin/omarchy-skill-hub" "$BIN_DIR/omarchy-skill-hub"
install -m755 "$SRC/bin/omarchy-skill-hubctl" "$BIN_DIR/omarchy-skill-hubctl"
mkdir -p "$HOME_DATA/icons/hicolor/scalable/apps"
install -m644 "$SRC/assets/omarchy-skill-hub.svg" "$HOME_DATA/icons/hicolor/scalable/apps/omarchy-skill-hub.svg"
cat > "$HOME_DATA/applications/omarchy-skill-hub.desktop" <<EOT
[Desktop Entry]
Type=Application
Name=Omarchy Skill Hub
Comment=Manage and assign local AI skills
Exec=$BIN_DIR/omarchy-skill-hub
Icon=omarchy-skill-hub
Terminal=false
Categories=Development;Utility;
Actions=Open;
[Desktop Action Open]
Name=Open native Skill Hub
Exec=$BIN_DIR/omarchy-skill-hub
EOT
printf '\nBackend installed at %s\nNative panel: omarchy-skill-hub\n' "$DEST"
printf 'Omarchy Quattro widget: run omarchy plugin add <repository-url> --enable\n'
